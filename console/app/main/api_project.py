from . import main
from flask import jsonify, request
from flask_login import login_required
from .func import *
from ..models import User


@main.route('/project/user/<int:uid>')
@login_required
def get_project_user(uid):
    user = User.query.get_or_404(uid)
    if user.is_admin:
        project_list = Project.query.all()
    else:
        if not user.group_user_id:
            project_list = Project.query.filter(Project.user_id == uid).all()
        else:
            project_list = Project.query.filter(Project.user_id == user.group_user_id).all()

    projects = [v.project_name for v in project_list if v.project_name]
    return jsonify({'data': projects})
