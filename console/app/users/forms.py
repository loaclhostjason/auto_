# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo
from ..base import BaseForm


class UserPasswordForm(FlaskForm, BaseForm):
    upw = PasswordField('新密码:', validators=[DataRequired(message='新密码不能为空！'), EqualTo('upw2', message='密码不一致')])
    upw2 = PasswordField('确认密码:', validators=[DataRequired(message='确认密码不能为空！')])


class UserForm(UserPasswordForm):
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(meta={'csrf': False}, *args, **kwargs)

    username = StringField('用户账号:', validators=[DataRequired(message='用户账号不能为空')])
    expiry_time = StringField('过期时间:', validators=[DataRequired('过期时间不能为空')])
    submit = SubmitField('确认')

    def get_user_form(self):
        d = {
            'username': self.username.data,
            'expiry_time': '{} {}'.format(self.expiry_time.data, '23:59:59'),
            'password': self.upw.data,
            'role': 'user'
        }
        return d

    def validate_user_info(self):
        if not self.username.data:
            return '用户名不能为空'
        if not self.expiry_time.data:
            return '过期时间不能空'
        return

    def validate_user_pwd(self):
        if not self.upw.data:
            return '新密码不能为空'
        if not self.upw2.data:
            return '确认密码不能空'
        return
