from . import manage
from flask_login import login_required
from flask import request, jsonify
from .models import Attr
from sqlalchemy import or_
import json
from .models import *


@manage.route('/attr/content/add', methods=['POST'])
@login_required
def add_attr_content():
    project_id = request.args.get('project_id')
    level = request.form.get('level')
    project_relation_id = request.form.get('project_relation_id')

    if not project_id or not project_relation_id or not level:
        return jsonify({'success': False, 'message': '提交参数缺失'})

    form_data = request.form.to_dict()

    attr = Attr.query.filter_by(level=level).first()

    content = json.loads(attr.content) if attr and attr.content else []
    result = [(info['item'], info['item_zh']) for info in content if info.get('item_required')]

    if result:
        for r, r_name in result:
            if not form_data.get(r):
                return jsonify({'success': False, 'message': '请检查【%s】，是否必须填写' % r_name})

    AttrContent.create_edit(form_data, project_id, project_relation_id)
    return jsonify({'success': True, 'message': '更新成功'})
