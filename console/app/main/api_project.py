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
        project_list = Project.query.filter(Project.name == user.project_name).all()

    projects = [v.project_name for v in project_list if v.project_name]
    projects = sorted(set(projects), key=projects.index)
    return jsonify({'data': projects})
