# -*- coding: utf-8 -*-
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask import request, current_app
from flask_login import current_user
from datetime import datetime
from . import db, login_manager

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from enum import Enum
from collections import defaultdict, OrderedDict
import json


class RoleType(Enum):
    admin = '超级管理员'
    user = '普通用户'
    project_user = '项目管理员'


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    display_name = db.Column(db.String(64))
    password_hash = db.Column(db.String(128))
    login_ip = db.Column(db.String(32))
    login_time = db.Column(db.DateTime())
    register_time = db.Column(db.DateTime(), default=datetime.now)

    role = db.Column(db.Enum(RoleType), nullable=False)

    expiry_time = db.Column(db.DateTime)

    project_group_id = db.Column(db.Integer, db.ForeignKey('project_group.id'))
    project_group = db.relationship('ProjectGroup', backref=db.backref("users"))

    project_id = db.Column(db.Integer, index=True)

    # group_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    # user = db.relationship('User', remote_side='User.id', backref=db.backref("users", cascade="all, delete-orphan"))

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return bool(self.username == 'admin')

    @property
    def is_pm_admin(self):
        return bool(self.role.name == 'project_user')

    @property
    def is_expiry(self):
        now = datetime.now()
        if not self.expiry_time:
            return
        dif_time = (self.expiry_time - now).days
        return dif_time

    @classmethod
    def update_time_ip(cls):
        user = cls.query.filter(cls.username == current_user.username).first_or_404()
        user.login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user.login_ip = request.remote_addr
        db.session.add(user)

    def to_dict(self):
        d = {
            'username': self.username,
            'expiry_time': self.expiry_time.strftime('%Y-%m-%d') if self.expiry_time else ''
        }
        return d

    @staticmethod
    def insert_admin():
        u = {
            'username': 'admin',
            'password': '123',
            'role': 'admin',
        }
        old = User.query.filter_by(username=u['username']).first()
        if not old:
            db.session.add(User(**u))
            db.session.commit()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Modification(db.Model):
    __tablename__ = 'modification'
    id = db.Column(db.Integer, primary_key=True)

    content = db.Column(db.Text)
    default_conf = db.Column(db.Text)

    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    project = db.relationship('Project', backref=db.backref("modification", cascade="all, delete-orphan"))

    def to_json(self):
        result = self.to_dict()
        del result['id']
        result['project_id'] = None
        return result

    @staticmethod
    def set_default_conf(project_id, ext_default=False):
        from .main.models import ProjectRelation, ProjectData, AttrContent
        data = ProjectData.query.filter(ProjectData.project_id == project_id,
                                        ProjectData.default_conf.isnot(None)).all()
        default_ = dict()
        if data:
            for d in data:
                parent_relation = ProjectRelation.query.get_or_404(d.project_relation_id)

                bit_line, start_bit, byte_info = AttrContent.get_attr_info(d.project_relation_id)

                if d.default_conf:
                    if (bit_line + start_bit) <= 8:
                        default_[parent_relation.parent_id] = d.default_conf
                    else:
                        if ext_default:
                            default_[parent_relation.parent_id] = d.default_conf[-(bit_line + start_bit - 8):]
                        else:
                            default_[parent_relation.parent_id] = d.default_conf[:-(bit_line + start_bit - 8)]
        return default_

    def set_content(self, project_id):
        from .main.models import ProjectRelation, ProjectData, AttrContent
        from console.util import ExportXml

        export_xml = ExportXml(project_id)

        conf_data = defaultdict(list)
        ext_conf_data = dict()
        new_relation = defaultdict(list)
        _ext_conf_data = {
            'info': '',
            'data': []
        }

        project = ProjectData.query.filter_by(project_id=project_id).order_by(ProjectData.project_relation_id).all()
        if project:
            for pro in project:
                parent_relation = ProjectRelation.query.get_or_404(pro.project_relation_id)
                pev_did = ProjectRelation.query.filter_by(id=parent_relation.parent_id).first()

                bit_line, start_bit, byte_info, ext_bit, parameter_name = AttrContent.get_attr_info(
                    pro.project_relation_id,
                    show_param=True)
                bit_info = {
                    'bit_len': bit_line,
                    'start_bit': start_bit,
                    'byte_info': byte_info,
                    'ext_bit': ext_bit,
                    'parameter_name': parameter_name,
                }

                conf_datas = ProjectData().conf_data(pro.content, project_id, pev_did.parent_id, bit_info, pro.las)
                # print(conf_datas)
                new_relation[parent_relation.parent_id].append(int(pro.project_relation_id))
                if conf_datas:
                    for index, cd_info in enumerate(conf_datas):
                        if index == 0:
                            if len(conf_datas) >= 1:
                                cd_info = cd_info if cd_info else '0'
                            conf_data[parent_relation.parent_id].append((export_xml.str_to_hex(cd_info), pro.las))
                        else:
                            cd_info = cd_info if cd_info else '0'
                            if str(pro.las).lower() != 'all':
                                ext_config_data = (export_xml.str_to_hex(cd_info), pro.las)
                                default_conf = self.set_default_conf(project_id, ext_default=True)
                                default_val = default_conf.get(parent_relation.parent_id, '')

                                _ext_conf_data['info'] = export_xml.get_ext_conf_data(bit_info, default_val)
                                _ext_conf_data['data'].append(ext_config_data)
                                ext_conf_data[parent_relation.id] = _ext_conf_data

        ext_conf_data = {
            k: [ext_conf_data[val] for val in v if ext_conf_data.get(val)] for k, v in new_relation.items()}

        ext_conf_data = {k: v for k, v in ext_conf_data.items() if v}

        result = {
            'conf_data': conf_data,
            'ext_conf_data': ext_conf_data,
        }
        return result

    @classmethod
    def add_edit(cls, project_id):
        modification = cls.query.filter(cls.project_id == project_id).first()

        default_conf = cls.set_default_conf(project_id)
        content = cls().set_content(project_id)

        if modification:
            modification.content = json.dumps(content or {})
            modification.default_conf = json.dumps(default_conf or {})
        else:
            d = {
                'project_id': project_id,
                'default_conf': json.dumps(default_conf or {}),
                'content': json.dumps(content or {}),
            }
            modification = cls(**d)

        db.session.add(modification)
        db.session.commit()
