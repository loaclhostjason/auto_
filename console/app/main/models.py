from .. import db
from datetime import datetime
from enum import Enum


class ProjectRelationType(Enum):
    worker = '工作树'
    func = '功能树'


class Project(db.Model):
    __tablename__ = 'project'
    id = db.Column(db.Integer, primary_key=True)
    # 名称
    name = db.Column(db.String(68), index=True)

    first_time = db.Column(db.DateTime, default=datetime.now)
    last_time = db.Column(db.DateTime, default=datetime.now)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', backref=db.backref("project", cascade="all,delete"))

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
        return result
