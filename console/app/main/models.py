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

    def to_json(self, user_id=None):
        d = self.to_dict()
        if d.get('first_time'):
            del d['first_time']
        if d.get('last_time'):
            del d['last_time']

        d['user_id'] = user_id
        del d['id']
        return d


class ProjectRelation(db.Model):
    __tablename__ = 'project_relation'
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, index=True)

    # 名称
    name = db.Column(db.String(32), index=True)
    level = db.Column(db.Integer, default=1, nullable=False, index=True)
    type = db.Column(db.Enum(ProjectRelationType), default='worker', nullable=False)

    timestamp = db.Column(db.DateTime, default=datetime.now)

    relation_order = db.Column(db.Integer, default=1, index=True)

    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    project = db.relationship('Project', backref=db.backref("project_relation", cascade="all, delete-orphan"))

    def __init__(self, *args, **kwargs):
        super(ProjectRelation, self).__init__(*args, **kwargs)

    def to_json(self, remove_key=None):
        d = self.to_dict()
        if d.get('timestamp'):
            del d['timestamp']

        d['attr'] = None
        d['extra_attr'] = None
        d['project_id'] = None
        d['parent_id'] = None
        d['child'] = list()

        # ext
        if self.level == 3:
            d['default_conf'] = None
            d['conf_data'] = None
            d['ext_conf_data'] = None

        if remove_key:
            for rk in remove_key:
                try:
                    del d[rk]
                except Exception as e:
                    print(e)
                    pass
        return d

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
    las = db.Column(db.String(10280))
    name = db.Column(db.String(200))

    content = db.Column(db.Text)
    # real_content = db.Column(db.Text)

    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    default_conf = db.Column(db.String(68))

    timestamp = db.Column(db.DateTime, default=datetime.now)
    project = db.relationship('Project', backref=db.backref("project_data", cascade="all, delete-orphan"))
    project_relation = db.relationship('ProjectRelation',
                                       backref=db.backref("project_data", cascade="all, delete-orphan"))

    def to_json(self, remove_key=None):
        d = self.to_dict()
        if d.get('timestamp'):
            del d['timestamp']

        if remove_key:
            for rk in remove_key:
                try:
                    del d[rk]
                except Exception as e:
                    print(e)
                    pass

        d['attr'] = None
        d['extra_attr'] = None
        d['project_id'] = None
        d['project_relation_id'] = None
        return d

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

    def conf_data(self, content, project_id, did_relation_id, bit_info, las):
        did_len = self.p_did_len(project_id, did_relation_id)
        # print(did_len)
        if not content or not did_len:
            return

        content = json.loads(content)

        result = []
        extra_key = ['byte{}'.format(v) for v in range(did_len)]

        real_bit_len = bit_info['start_bit'] + bit_info['bit_len']

        extra_key = [v for v in extra_key if content.get(v)]

        if las and str(las).lower() == 'all' and not extra_key:
            result.append('0')
            extra_key = True

        if not extra_key:
            return
        # print(extra_key)
        if extra_key and isinstance(extra_key, list):
            for index, key in enumerate(extra_key):
                if real_bit_len > 8:
                    b_len = real_bit_len - 8
                    b1 = content[key][:-b_len]
                    b2 = content[key][-b_len:]
                    result = [b1, b2]
                else:
                    result.append(content[key])
        return result

    @staticmethod
    def init_key(str_key):
        key = []
        for index in range(8):
            key.append('%s_%s' % (str_key, index))
        return key

    def _get_bitwidth(self, start_bit, ext_bit, len_bit):
        bitwidth = []
        index = 0
        while len_bit > 0:
            '''if len_bit + start_bit >= 8:
                bitwidth.append(8 - start_bit)
            else:
                bitwidth.append(len_bit - start_bit)'''
            if index == 0:
                if len_bit + start_bit < 8:
                    bitwidth.append(len_bit)
                else:
                    bitwidth.append(8 - start_bit)
            else:
                if ext_bit >= 8:
                    bitwidth.append(0)
                    len_bit = 0
                else:
                    if len_bit > 8 - ext_bit:
                        bitwidth.append(8 - ext_bit)
                    else:
                        bitwidth.append(len_bit)
            len_bit = len_bit - bitwidth[index]
            #start_bit = 0
            index = index + 1
        return bitwidth

    def get_content(self, project_id, did_relation_id, relation_id=None):
        from .api_data import split_default_val

        did_len = self.p_did_len(project_id, did_relation_id)
        bit_len, *args = AttrContent.get_attr_info(relation_id, is_parent=True, show_ext_bit=True)

        bit_width = self._get_bitwidth(args[0], args[2], bit_len)

        key = list()
        if not did_len:
            return list(), []

        extra_key = ['byte{}'.format(v) for v in range(did_len)]

        key.extend(extra_key)

        project_relation_id = request.form.getlist('project_relation_id')
        result = []
        # print(project_relation_id)

        default_val = None
        default_conf = None
        strInfo = ''
        for index, val in enumerate(project_relation_id):
            d = {
                'project_id': project_id,
                'project_relation_id': val,
                'content': {},
            }
            bit_width_index = 0
            fill_value = ''
            for v in key:
                d['las'] = request.form.getlist('las')[index]
                d['name'] = request.form.getlist('name')[index]

                if d['las'].lower() == 'all' and request.form.get('%s_%s' % (val, v)):
                    default_val = request.form.get('%s_%s' % (val, v))
                    default_conf = request.form.get('default_conf')

                # if request.form.get('%s_%s' % (val, v)):
                if request.form.get('%s_%s' % (val, v)):
                    _this_val = request.form.get('%s_%s' % (val, v))
                    d['content'][v] = _this_val  #split_default_val(_this_val, bit_len)
                    if len(_this_val) < bit_width[bit_width_index]: #bit_len:
                        strInfo += '%s 行 %s 数据输入不足%d\r\n' %(d['las'], v, bit_width[bit_width_index])
                    fill_value = fill_value + _this_val
                    bit_width_index = bit_width_index + 1
                else:
                    byteData = request.form.getlist('%s_%s' % (val, v))
                    if  len(byteData) > 0 and byteData[0] == '':
                        strInfo += '%s 行 %s 数据输入不足%d\r\n' % (d['las'], v, bit_width[bit_width_index])
                    d['content'][v] = ''

            result.append(d)
            if d['las'].lower() == 'all' and default_conf and fill_value != default_conf:
                strInfo += '第 %d (ALL)行数据与默认值不一致' %(index + 1)
        return [v for v in result if v.get('content')], default_val, strInfo


class ProjectGroup(db.Model):
    __tablename__ = 'project_group'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))


class ProjectPartNumber(db.Model):
    __tablename__ = 'project_part_number'
    id = db.Column(db.Integer, primary_key=True)

    number = db.Column(db.String(120))
    las = db.Column(db.String(120))

    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    project = db.relationship('Project', backref=db.backref("part_number", cascade="all, delete-orphan"))

    part_num_relation_id = db.Column(db.Integer, db.ForeignKey('project_part_number_relation.id'))
    part_num_relation = db.relationship('ProjectPartNumRelation', backref=db.backref("part_number", cascade="all"))

    def to_json(self):
        data = self.to_dict()
        del data['id']
        data['project_id'] = None
        data['part_num_relation_id'] = None
        return data


class ProjectPartNumberAttr(db.Model):
    __tablename__ = 'project_part_number_attr'
    id = db.Column(db.Integer, primary_key=True)

    did = db.Column(db.String(120))
    name = db.Column(db.String(120))

    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    project = db.relationship('Project', backref=db.backref("part_number_attr", cascade="all, delete-orphan"))

    part_num_relation_id = db.Column(db.Integer, db.ForeignKey('project_part_number_relation.id'))
    part_num_relation = db.relationship('ProjectPartNumRelation', backref=db.backref("part_number_attr", cascade="all"))

    def to_json(self):
        data = self.to_dict()
        del data['id']
        data['project_id'] = None
        data['part_num_relation_id'] = None
        return data


class ProjectPartNumRelation(db.Model):
    __tablename__ = 'project_part_number_relation'
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, index=True)

    # 名称
    name = db.Column(db.String(32), index=True)
    level = db.Column(db.Integer, default=1, nullable=False, index=True)

    relation_order = db.Column(db.Integer, default=1, index=True)

    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    project = db.relationship('Project', backref=db.backref("project_part_number_relation", cascade="all"))

    def __init__(self, *args, **kwargs):
        super(ProjectPartNumRelation, self).__init__(*args, **kwargs)

    def to_json(self, remove_key=None):
        data = self.to_dict()
        data['child'] = list()
        data['part'] = list()
        data['attr'] = None
        if remove_key:
            for rk in remove_key:
                try:
                    del data[rk]
                except Exception as e:
                    print(e)
                    pass
        data['project_id'] = None
        data['parent_id'] = None
        return data

    @classmethod
    def add_info(cls, data):
        if not data:
            return
        r = cls(name=data.name, project_id=data.id)
        db.session.add(r)
        db.session.commit()
        return r

    @classmethod
    def add_part_relation(cls, data, content, project_id):
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
