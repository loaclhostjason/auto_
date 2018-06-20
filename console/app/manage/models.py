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
    real_content = db.Column(db.Text)

    username = db.Column(db.String(12), default='系统')
