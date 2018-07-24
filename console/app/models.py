# -*- coding: utf-8 -*-
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask import request, current_app
from flask_login import current_user
from datetime import datetime
from . import db, login_manager

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from enum import Enum


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

    project_name = db.Column(db.String(100))

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
