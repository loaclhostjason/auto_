# coding: utf-8
from flask import render_template, redirect, url_for, jsonify, abort, request, flash, current_app
from flask_login import login_required

from . import users
from .forms import *
from ..base import Check
from ..app import upload_files
from config import Config
import os
from datetime import datetime
from ..models import *
from ..decorators import role_admin_pm


@users.route('/')
@login_required
@role_admin_pm
def users_list():
    form = UserForm()
    # users = User.query.filter(User.group_user_id.is_(None)).all()
    users = User.query.all()
    return render_template('users/users_list.html', users=users, form=form)
