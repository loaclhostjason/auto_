from . import main
from flask import jsonify, request
from flask_login import login_required, current_user
# from .models import *
from .func import *
from ..manage.models import *
import json


# main attr content
@main.route('/project/data/get', methods=['GET', 'POST'])
@login_required
def option_project_data():
    # get attr 参数
    project_id = request.args.get('project_id')
    parent_id = request.args.get('project_relation_id')
    if not project_id or not parent_id:
        return jsonify({'success': False, 'message': '参数不对'})

    result = get_project_children_v2(project_id, int(parent_id))
    project_data = ProjectData.query.filter_by(project_id=project_id).all()
    project_data = {v.project_relation_id: v.to_dict(
        extra_dict={'content': json.loads(v.content) if v.content else {}}) for v in project_data}
    return jsonify({'success': True, 'result': result, 'project_data': project_data})
