from . import manage
from flask_login import login_required
from flask import request, jsonify
from .models import Attr
from sqlalchemy import or_
import json
from .models import *
from ..main.models import ProjectRelation, Project
import math
from ..main.models import ProjectData
from ..models import Modification


@manage.route('/attr/content/add', methods=['POST'])
@login_required
def add_attr_content():
    project_id = request.args.get('project_id')
    level = request.form.get('level')
    project_relation_id = request.form.get('project_relation_id')

    if not project_id or not project_relation_id or not level:
        return jsonify({'success': False, 'message': '提交参数缺失'})

    # this is byte len
    project_relation = ProjectRelation.query.get_or_404(project_relation_id)
    prev_pr = ProjectRelation.query.filter_by(id=project_relation.parent_id).first()
    prev_attr_content = AttrContent.query.filter_by(project_relation_id=prev_pr.id if prev_pr else 0).first()
    did_byte_len = json.loads(prev_attr_content.real_content).get('DidLength',
                                                                  0) if prev_attr_content and prev_attr_content.real_content else 0

    byte_val = 0
    if prev_attr_content and prev_attr_content.real_content:
        byte_val = json.loads(prev_attr_content.real_content).get('BytePosition', 0)

    form_data = request.form.to_dict()

    attr = Attr.query.filter_by(level=level).first()

    content = json.loads(attr.content) if attr and attr.content else []
    result = [info['item'] for info in content if info.get('item_required')]

    if result:
        for r in result:
            if not form_data.get(r):
                return jsonify({'success': False, 'message': '请检查【%s】，是否必须填写' % r})

    if form_data.get('BytePosition') and int(form_data['BytePosition']) > int(did_byte_len):
        return jsonify({'success': False, 'message': 'BytePositionc 数字在0-%s之间' % int(did_byte_len)})

    if form_data.get('BitPosition') and int(form_data['BitPosition']) > 7:
        return jsonify({'success': False, 'message': 'BitPosition 在0-7之间'})

    if form_data.get('BitLength'):
        input_number = 16 - int(form_data['BitPosition'])
        if int(form_data['BitLength']) > input_number:
            return jsonify({'success': False, 'message': '只能跨2个字节，BitLength 请输入小于等于%d数字' % input_number})

    AttrContent.create_edit(form_data, project_id, project_relation_id)

    update_project_config_name(form_data, project_id)

    if level and int(level) == 3:
        Modification.add_edit(project_id)

    # change byte project data
    if form_data.get('BytePosition') and int(form_data['BytePosition']) != int(byte_val):
        pd_ids = ProjectRelation.query.filter_by(parent_id=project_relation.id).all()
        pd_ids = [v.id for v in pd_ids]
        print(pd_ids)
        project_data = ProjectData.query.filter(ProjectData.project_relation_id.in_(pd_ids) if pd_ids else False).all()
        if project_data:
            for pd in project_data:
                pd.content = json.dumps({})
                db.session.add(pd)

    return jsonify({'success': True, 'message': '更新成功'})


# update project file name
def update_project_config_name(form_data, project_id):
    project_config_name = form_data.get('ConfigurationFileNumber')
    if project_config_name:
        project = Project.query.filter_by(id=project_id).first()
        if project:
            project.project_config_name = project_config_name
            db.session.add(project)
