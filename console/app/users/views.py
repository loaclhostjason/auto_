# coding: utf-8
from flask import render_template, redirect, url_for, jsonify, abort, request, flash, current_app
from flask_login import login_required

from . import users
from .forms import *
from ..base import Check
from ..app import upload_files
from console.config import Config
import os
from datetime import datetime
from ..models import *
from ..decorators import role_admin_pm
from sqlalchemy import or_, and_


@users.route('/')
@login_required
@role_admin_pm
def users_list():
    form = UserForm()
    # users = User.query.filter(User.group_user_id.is_(None)).all()
    if current_user.is_admin:
        users = User.query.all()
    else:
        users = User.query.filter(
            or_(and_(User.project_group_id == current_user.project_group_id, User.role == 'user'),
                User.id == current_user.id)).all()

    return render_template('users/users_list.html', users=users, form=form)
