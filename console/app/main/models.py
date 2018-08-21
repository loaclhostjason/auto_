from .. import db
from datetime import datetime
from enum import Enum
from flask import request
import json
from ..manage.models import AttrContent
import math


class ProjectRelationType(Enum):
    worker = '工作树'
    func = '功能树'


class Project(db.Model):
    __tablename__ = 'project'
    id = db.Column(db.Integer, primary_key=True)
    # 文件名称
    name = db.Column(db.String(68), index=True)
    # 项目名称
    # project_name = db.Column(db.String(68), index=True)
    project_group_id = db.Column(db.Integer, db.ForeignKey('project_group.id'))

    first_time = db.Column(db.DateTime, default=datetime.now)
    last_time = db.Column(db.DateTime, default=datetime.now)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', backref=db.backref("project", cascade="all, delete"))
    project_group = db.relationship('ProjectGroup', backref=db.backref("project"))

    project_config_name = db.Column(db.String(100))

    def __init__(self, *args, **kwargs):
        super(Project, self).__init__(*args, **kwargs)


class ProjectRelation(db.Model):
    __tablename__ = 'project_relation'
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, index=True)

    # 名称
    name = db.Column(db.String(32))
    level = db.Column(db.Integer, default=1, nullable=False)
    type = db.Column(db.Enum(ProjectRelationType), default='worker', nullable=False)

    timestamp = db.Column(db.DateTime, default=datetime.now)

    relation_order = db.Column(db.Integer, default=1)

    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    project = db.relationship('Project', backref=db.backref("project_relation", cascade="all, delete-orphan"))

    def __init__(self, *args, **kwargs):
        super(ProjectRelation, self).__init__(*args, **kwargs)

    @classmethod
    def add_project_relation(cls, data, content, project_id):
        max_order = cls.query.filter(cls.project_id == project_id, cls.parent_id == data['parent_id']). \
            order_by(cls.relation_order.desc(), cls.id.desc()).first()
        result = []
        for index, name in enumerate(content.split('\r\n'), start=max_order.relation_order + 1 if max_order else 1):
            if name:
                data['relation_order'] = index
                data['name'] = name
                result.append(cls(**data))

        db.session.add_all(result)
        db.session.flush()
        result = [v.id for v in result]
        db.session.commit()
        return result


class ProjectData(db.Model):
    __tablename__ = 'project_data'
    id = db.Column(db.Integer, primary_key=True)
    project_relation_id = db.Column(db.Integer, db.ForeignKey('project_relation.id'))
    las = db.Column(db.String(250))
    name = db.Column(db.String(32))

    content = db.Column(db.Text)
    # real_content = db.Column(db.Text)

    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    default_conf = db.Column(db.String(68))

    timestamp = db.Column(db.DateTime, default=datetime.now)
    project = db.relationship('Project', backref=db.backref("project_data", cascade="all, delete-orphan"))
    project_relation = db.relationship('ProjectRelation',
                                       backref=db.backref("project_data", cascade="all, delete-orphan"))

    @staticmethod
    def p_did_len(project_id, did_relation_id):
        attr = AttrContent.query.filter_by(project_id=project_id, project_relation_id=did_relation_id).all()
        d = dict()
        if attr:
            for info in attr:
                # print(info.real_content)
                content = json.loads(info.real_content or '{}')
                d.update(content)
        try:
            did_len = int(d.get('DidLength'))
        except:
            did_len = 0
        return did_len

    def conf_data(self, content, project_id, did_relation_id):
        did_len = self.p_did_len(project_id, did_relation_id)
        # print(did_len)
        if not content or not did_len:
            return

        content = json.loads(content)

        result = []
        extra_key = ['byte{}'.format(v) for v in range(did_len)]
        for key in extra_key:
            if content.get(key):
                result.append(content.get(key))
        return result

    @staticmethod
    def init_key(str_key):
        key = []
        for index in range(8):
            key.append('%s_%s' % (str_key, index))
        return key

    def get_content(self, project_id, did_relation_id):
        from .api_data import split_default_val

        did_len = self.p_did_len(project_id, did_relation_id)
        # print(did_len)
        key = list()
        if not did_len:
            return list()

        extra_key = ['byte{}'.format(v) for v in range(did_len)]

        key.extend(extra_key)

        project_relation_id = request.form.getlist('project_relation_id')
        result = []
        # print(project_relation_id)
        for index, val in enumerate(project_relation_id):
            d = {
                'project_id': project_id,
                'project_relation_id': val,
                'content': {},
            }
            for v in key:
                d['las'] = request.form.getlist('las')[index]
                d['name'] = request.form.getlist('name')[index]
                # if request.form.get('%s_%s' % (val, v)):
                if request.form.get('%s_%s' % (val, v)):

                    bit_len, start_bit, byte_info = AttrContent.get_attr_info(val)
                    _this_val = request.form.get('%s_%s' % (val, v))

                    print(v, _this_val)
                    d['content'][v] = _this_val
                    # d['content'][v] = split_default_val(_this_val, math.ceil(bit_len / (math.ceil((bit_len + start_bit) / 8) - 1)))
                else:
                    d['content'][v] = ''

            result.append(d)
        return [v for v in result if v.get('content')]


class ProjectGroup(db.Model):
    __tablename__ = 'project_group'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
