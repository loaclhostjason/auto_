from . import main
from flask import jsonify, request
from flask_login import login_required, current_user
# from .models import *
from .func import *
from ..manage.models import *
import json
from util import ExportXml


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

    did_len = 0
    if result:
        did_id = result[0]['level_2_id']
        attr_content = AttrContent.query.filter_by(project_relation_id=did_id).first()
        if attr_content and attr_content.real_content:
            real_content = json.loads(attr_content.real_content)
            did_len = real_content.get('DidLength') or 0
    return jsonify({'success': True, 'result': result, 'project_data': project_data, 'did_len': did_len})


# main attr content
@main.route('/project/data/submit/<int:project_id>', methods=['POST'])
@login_required
def edit_project_data_api(project_id):
    # get attr 参数
    data = ProjectData.get_content(project_id)
    if not data:
        return jsonify({'success': True, 'message': 'project_id不存在'})

    new_dict = dict()
    for v in data:
        new_dict[v['project_relation_id']] = v

    for project_relation_id, val in new_dict.items():
        val['content'] = json.dumps(val['content'])
        old_project_data = ProjectData.query.filter_by(project_relation_id=project_relation_id).first()
        if old_project_data:

            ProjectData.update_model(old_project_data, val)
        else:
            new_project_data = ProjectData(**val)
            db.session.add(new_project_data)

    ProjectData.update_real_content(project_id)
    export_xml = ExportXml(project_id)
    export_xml.run()
    return jsonify({'success': True, 'message': '更新成功'})
