from . import main
from flask import jsonify, request
from flask_login import login_required, current_user
# from .models import *
from .func import *
from ..manage.models import *
import json
from console.util import ExportXml
from ..models import Modification


# main attr content
@main.route('/project/data/get', methods=['GET', 'POST'])
@login_required
def option_project_data():
    # get attr 参数
    project_id = request.args.get('project_id')
    parent_id = request.args.get('project_relation_id')
    if not project_id or not parent_id:
        return jsonify({'success': False, 'message': '参数不对'})

    # this is byte len
    project_relation = ProjectRelation.query.get_or_404(parent_id)
    child_project_relation = ProjectRelation.query.filter_by(parent_id=parent_id).all()
    cpr_ids = [v.id for v in child_project_relation]

    prev_attr_content = AttrContent.query.filter_by(project_relation_id=project_relation.id).first()

    if prev_attr_content and prev_attr_content.real_content:
        real_content = json.loads(prev_attr_content.real_content)
    else:
        real_content = {}

    result = get_project_children_v2(project_id, int(parent_id))
    project_data = ProjectData.query.filter(ProjectData.project_id == project_id,
                                            ProjectData.project_relation_id.in_(cpr_ids) if cpr_ids else False).all()

    default_conf = [v.default_conf for v in project_data if v.default_conf]
    default_conf = list(set(default_conf))[0] if default_conf else None

    project_dict = dict()
    cot = real_content.copy()

    r1 = {
        'success': True,
        'level': project_relation.level,
        'result': result,
        'project_data': project_dict,
        'byte_position': cot.get('BytePosition'),
        'default_conf': default_conf,
        'ext_bitPosition': cot.get('ExtBitPosition')
    }
    if not real_content.get('BytePosition') or not real_content.get('BitPosition'):
        return jsonify(r1)

    if project_data:
        for v in project_data:
            if v.content:
                vv = {k: v for k, v in v.to_dict().items() if k != 'content'}
                c = json.loads(v.content)
                t = {k: v for k, v in c.items() if not k.startswith('bit')}
                byte_c = 'byte%s' % real_content['BytePosition']

                t[byte_c] = c.get(byte_c) or ''
                vv['content'] = t
                project_dict[v.project_relation_id] = vv

    did_len = 0
    if result:
        did_id = result[0]['level_2_id']
        attr_content = AttrContent.query.filter_by(project_relation_id=did_id).first()
        if attr_content and attr_content.real_content:
            real_content = json.loads(attr_content.real_content)
            did_len = real_content.get('DidLength') or 0

    bit_position = list()
    if cot.get('BitPosition') and cot.get('BitLength'):
        bit_start = int(cot['BitPosition'])
        len_x = int(cot['BitLength'])
        for index in range(len_x):
            bit_position.append(bit_start)
            bit_start += 1

    r2 = {
        'success': True,
        'result': result,
        'level': project_relation.level,
        'project_data': project_dict,
        'did_len': did_len,
        'bit_position': bit_position,
        'byte_position': cot.get('BytePosition'),
        'default_conf': default_conf,
        'ext_bitPosition': cot.get('ExtBitPosition')
    }
    return jsonify(r2)


def split_default_val(data, bit_len):
    if not data:
        return
    if len(data) == bit_len:
        return data

    if len(data) > bit_len:
        data = data[-bit_len:]
    else:
        data = ''.join(['0' for v in range(bit_len - len(data))]) + data
    return data


def get_default_conf(default_val=None):
    project_relation_id = request.form.getlist('project_relation_id')
    default_conf = request.form.get('default_conf')
    result = dict()
    if project_relation_id:
        for index, v in enumerate(project_relation_id):
            if default_conf:
                bit_len, *args = AttrContent.get_attr_info(v)
                if default_val:
                    result[v] = default_val if len(default_val) == bit_len else split_default_val(default_val, bit_len)
                else:
                    result[v] = default_conf if len(default_conf) == bit_len else split_default_val(default_conf,
                                                                                                    bit_len)

    return result


# main attr content
@main.route('/project/data/submit/<int:project_id>', methods=['POST'])
@login_required
def edit_project_data_api(project_id):
    from .test import update_default_val
    # get attr 参数
    data_relation_id = request.args.get('data_relation_id')
    if not data_relation_id:
        return jsonify({'success': False, 'message': '没数据，不能保持'})

    # print(request.form.getlist('las'))
    check_las = [v for v in request.form.getlist('las') if not v]
    if len(check_las):
        return jsonify({'success': False, 'message': 'LAS不能为空，如果保存请将空的LAS 填写 None'})

    project_relation = ProjectRelation.query.filter_by(id=data_relation_id).first()
    data, default_val, strInfo = ProjectData().get_content(project_id, project_relation.parent_id, project_relation.id)
    if strInfo != '':
        return jsonify({'success': False, 'message': strInfo})

    print(111, default_val)
    default_conf = get_default_conf(default_val)

    if not data:
        return jsonify({'success': False, 'message': 'DidLength 不存在，请检查'})

    new_dict = dict()
    for v in data:
        new_dict[v['project_relation_id']] = v

    print(default_conf)
    print(new_dict)
    has_las_all = False
    need_id = []
    for project_relation_id, val in new_dict.items():
        if val.get('las') and str(val['las']).lower() == 'all':
            has_las_all = True
        need_id.append(project_relation_id)
        val['content'] = json.dumps(val['content'])
        old_project_data = ProjectData.query.filter_by(project_relation_id=project_relation_id).first()
        if old_project_data:
            ProjectData.update_model(old_project_data, val)
            old_project_data.default_conf = default_conf.get(project_relation_id)
            db.session.add(old_project_data)
        else:
            val['default_conf'] = default_conf.get(project_relation_id)
            new_project_data = ProjectData(**val)
            db.session.add(new_project_data)

    # db.session.commit()
    # update_default_val(project_id, project_relation.parent_id)

    # export_xml = ExportXml(project_id)
    # export_xml.run()

    # 如果有all 保存更新 默认值
    if has_las_all:
        pass

    Modification.add_edit(project_id)
    return jsonify({'success': True, 'message': '更新成功'})


@main.route('/las/get')
@login_required
def get_las_info():
    from read_las_config import read_excel
    project_group_id = request.args.get('project_group_id')

    path = current_app.config['LAS_FILE_PATH_ROOT']
    las = Las.query.filter_by(project_group_id=project_group_id).first()

    if las and las.file:
        path = os.path.join(path, las.file)

    data = read_excel(path, las.file if las else None)
    return jsonify({'data': data})


# change project data las name
@main.route('/change/project/data/name', methods=['post'])
@login_required
def change_project_data_name():
    name = request.form.get('value')
    project_relation_id = request.form.get('pk')

    if not name or not project_relation_id:
        return jsonify({'success': False, 'message': '提交参数不对'})

    project_data = ProjectData.query.filter_by(project_relation_id=project_relation_id).first()
    project_relation = ProjectRelation.query.filter_by(id=project_relation_id).first()

    if not project_data or not project_relation:
        return jsonify({'success': False, 'message': '没有这条记录'})

    project_data.name = name
    db.session.add(project_data)

    project_relation.name = name
    db.session.add(project_relation)

    db.session.commit()
    return jsonify({'success': True, 'message': '更新成功'})
