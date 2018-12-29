# -*- coding: utf-8 -*-
from .app import db, create_app, login_manager

app = create_app()


@app.before_request
def before_request():
    from .auth.models import OperateLog
    from flask_login import current_user, logout_user
    from flask import request, redirect, url_for

    if not current_user.is_authenticated:
        return

    if not (request.url_rule and request.url_rule.rule.startswith('/auth')):
        if not OperateLog.is_can_login(current_user.id):
            logout_user()
            return redirect(url_for('auth.login'))
