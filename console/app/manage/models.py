from .. import db
from enum import Enum
from datetime import datetime


class AttrType(Enum):
    worker = '工作树'
    func = '功能树'


class Attr(db.Model):
    __tablename__ = 'attr'
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(16))
    level = db.Column(db.Integer)
    type = db.Column(db.Enum(AttrType))

    update_time = db.Column(db.DateTime, default=datetime.now)
    content = db.Column(db.Text)
    username = db.Column(db.String(12), default='系统')

    @classmethod
    def init_attr(cls):
        r = [
            {'name': '结构树节点-1', 'level': 1, 'type': 'worker'},
            {'name': '结构树节点-2', 'level': 2, 'type': 'worker'},
            {'name': '结构树节点-3', 'level': 3, 'type': 'worker'},
            {'name': '功能树节点', 'level': 4, 'type': 'func'},
        ]
        attr = Attr.query.all()
        if attr:
            return
        result = []
        for info in r:
            new_attr = cls(**info)
            result.append(new_attr)
        db.session.add_all(result)
        db.session.commit()
        return


class AttrContent(db.Model):
    __tablename__ = 'attr_content'
    id = db.Column(db.Integer, primary_key=True)
    project_relation_id = db.Column(db.Integer, db.ForeignKey('project_relation.id'))

    real_content = db.Column(db.Text)

    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))

    project = db.relationship('Project', backref=db.backref("attr_content", cascade="all, delete-orphan"))
    project_relation = db.relationship('ProjectRelation',
                                       backref=db.backref("attr_content", cascade="all, delete-orphan"))
