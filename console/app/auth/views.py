# coding: utf-8
from flask import render_template, redirect, url_for, abort, request, flash, jsonify
from flask_login import login_user, current_user, login_required, logout_user
from . import auth
from .forms import *
from ..base import Check
from .models import *


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    Check(form).check_validate_on_submit()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if not user:
            flash({'errors': '用户名或者密码错误！'})
            return redirect(request.url)

        if user.is_expiry is not None and user.is_expiry < 0:
            flash({'errors': '已过期，无法登陆，请联系管理员'})
            return redirect(request.url)

        if user and user.verify_password(form.password.data):
            if not OperateLog.is_can_login(user.id):
                flash({'errors': '账号在另一台电脑上登录，无法登陆'})
                return redirect(request.url)

            login_user(user, True)
            current_user.update_time_ip()
            OperateLog.add_operate_log(user.id, '登录')
            return redirect(request.args.get('next') or url_for('main.projects'))
        flash({'errors': '用户名或者密码错误！'})

    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    OperateLog.add_operate_log(current_user.id, '注销')
    logout_user()
    return redirect(url_for('auth.login'))
