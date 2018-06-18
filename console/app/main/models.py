from .. import db
from datetime import datetime


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

    # todo delete
    timestamp = db.Column(db.DateTime, default=datetime.now)

    relation_order = db.Column(db.Integer, default=0)

    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    project = db.relationship('Project', backref=db.backref("project_relation", cascade="all, delete-orphan"))

    def __init__(self, *args, **kwargs):
        super(ProjectRelation, self).__init__(*args, **kwargs)
