from .. import db
from datetime import datetime
from flask import request


class OperateLog(db.Model):
    __tablename__ = 'operate_log'
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime, default=datetime.now)
    login_ip = db.Column(db.String(16), index=True)
    username = db.Column(db.String(32), index=True)
    action = db.Column(db.String(10))
    result = db.Column(db.String(32))
    message = db.Column(db.String(100))

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', backref=db.backref('operate_log', cascade='all, delete-orphan'))

    @classmethod
    def add_operate_log(cls, user_id=None, action=None, message=None, result='成功'):
        login_ip = request.remote_addr
        d = {
            'user_id': user_id,
            'login_ip': login_ip,
            'action': action,
            'message': message,
            'result': result
        }
        operation_log = OperateLog(**d)
        db.session.add(operation_log)

    @classmethod
    def is_can_login(cls, user_id):
        ip = request.remote_addr
        before_login = cls.before_login(user_id, ip)
        if before_login:
            return before_login

        last_info_query = cls.query.order_by(cls.time.desc(), cls.id.desc()).filter_by(user_id=user_id)
        last_info = last_info_query.first()
        if not last_info:
            return True

        last_ip_info = last_info_query.filter_by(login_ip=ip).first()
        if not last_ip_info:
            return bool(last_info.action == '注销')

        if last_ip_info.action == '注销':
            return True

        return False

    @classmethod
    def before_login(cls, user_id, ip):
        last_info = cls.query.order_by(cls.time.desc(), cls.id.desc()).filter_by(user_id=user_id, login_ip=ip).first()

        if last_info and last_info.action == '登录':
            return True
