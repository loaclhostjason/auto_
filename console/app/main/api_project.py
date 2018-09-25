from . import main
from flask import jsonify, request
from flask_login import login_required
from .func import *
from ..models import User


@main.route('/project/group/pm')
@login_required
def get_project_user():
    user_id = request.args.get('user_id')
    project_groups_query = ProjectGroup.query

    if user_id:
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return jsonify({'success': False, 'message': 'no user id'})

        project_groups = user.project_group if user.role.name != 'admin' else project_groups_query.all()
    else:
        project_groups = project_groups_query.all()

    try:
        project_groups = [(v.id, v.name) for v in project_groups]
    except Exception as e:
        project_groups = [(project_groups.id, project_groups.name)]
    return jsonify({'data': project_groups})


@main.route('/project/group/file')
@login_required
def get_project_user_file():
    project_group_id = request.args.get('project_group_id')
    project_query = Project.query

    if project_group_id:
        projects = project_query.filter(Project.project_group_id == project_group_id).all()
    else:
        projects = []

    projects = [(v.id, v.name) for v in projects if v.id]

    return jsonify({'data': projects})
