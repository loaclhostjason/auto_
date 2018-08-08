from .. import db
from datetime import datetime
from enum import Enum
from flask import request
import json


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

    @property
    def conf_data(self):
        if not self.content:
            return

        content = json.loads(self.content)
        extra_key = [
            'byte0', 'byte1', 'byte2', 'byte3'
        ]
        for key in extra_key:
            if content.get(key):
                return content[key]
        return

    @staticmethod
    def init_key(str_key):
        key = []
        for index in range(8):
            key.append('%s_%s' % (str_key, index))
        return key

    @classmethod
    def get_content(cls, project_id):
        bit0 = cls.init_key('bit0')
        bit1 = cls.init_key('bit1')
        bit2 = cls.init_key('bit2')
        bit3 = cls.init_key('bit3')

        extra_key = [
            'byte0', 'byte1', 'byte2', 'byte3'
        ]

        key = bit0 + bit1 + bit2 + bit3 + extra_key

        project_relation_id = request.form.getlist('project_relation_id')
        result = []
        print(project_relation_id)
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
                d['content'][v] = request.form.get('%s_%s' % (val, v)) or ''

            result.append(d)
        return [v for v in result if v.get('content')]

    @classmethod
    def update_real_content(cls, project_id):
        db.session.commit()
        project_data = cls.query.filter_by(project_id=project_id).all()
        if not project_data:
            return

        result = []
        for data in project_data:
            content = json.loads(data.content) if data.content else None
            if content:
                for index in range(3):
                    if content.get('byte%s' % index):
                        result.append(data.name)
                        result.append(data.las)
                        result.append('byte%s' % index)
                        for loop in range(8):
                            if content.get('bit%s_%s' % (index, loop)):
                                result.append('bit%s' % loop)
                        result.append(content.get('byte%s' % index))

            data.real_content = ';'.join(result)
            print(';'.join(result))
            db.session.add(data)


class ProjectGroup(db.Model):
    __tablename__ = 'project_group'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
