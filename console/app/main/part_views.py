from . import main
from flask_login import login_required
from flask import render_template, jsonify

from .models import *


@main.route('/project/part/number/edit/<int:project_id>', methods=['GET', 'POST'])
@login_required
def edit_part_num(project_id):
    project = Project.query.get_or_404(project_id)

    part_relation = ProjectPartNumRelation.query.filter_by(project_id=project_id).first()
    if not part_relation:
        ProjectPartNumRelation.add_info(project)

    return render_template('main/create_edit_part_number.html', project=project)


# project tree
@main.route('/part/number/tree')
@login_required
def get_part_number_tree():
    result = {
        'nodedata': [],
        'linkdata': [],
    }

    project_id = request.args.get('project_id')
    if not project_id:
        return jsonify({'success': False, 'message': '没有获取到配置文件信息'})

    part_relations_query = ProjectPartNumRelation.query.order_by(ProjectPartNumRelation.relation_order,
                                                                 ProjectPartNumRelation.id)
    part_relations = part_relations_query.filter_by(project_id=project_id).all()

    if not part_relations:
        return jsonify({'success': True, 'data': result})

    link_data = []
    for relation in part_relations:
        if relation.parent_id:
            link_data.append({'from': relation.parent_id, 'to': relation.id})

        result['nodedata'].append({
            'name': relation.name,
            'key': relation.id,
            'level': relation.level,
            'category': 'FirstNode' if relation.level == 1 else 'SecondNode'
        })

    result['linkdata'] = link_data
    return jsonify({'success': True, 'data': result})


@main.route('/part/number/content/add/<int:id>', methods=['POST'])
@login_required
def add_part_number_content(id):
    from .func import get_copy_part_info
    form_data = request.form.to_dict()

    action = request.args.get('action')

    if not form_data.get('content'):
        return jsonify({'success': False, 'message': '内容不能为空'})

    d = {
        'parent_id': form_data.get('parent_id'),
        'project_id': id,
        'level': form_data.get('level'),
    }
    if action == 'copy':
        copy_id = request.args.get('copy_id')
        info = get_copy_part_info(copy_id)
        if not info:
            return jsonify({'success': False, 'message': '不能复制'})
        d = {
            'parent_id': info.parent_id,
            'project_id': id,
            'level': info.level,
        }
        form_data['content'] = info.name

    ProjectPartNumRelation.add_part_relation(d, form_data['content'], id)
    return jsonify({'success': True, 'type': form_data.get('type')})


@main.route('/project/part/number/get')
@login_required
def project_part_number():
    # get attr 参数
    project_id = request.args.get('project_id')
    part_num_relation_id = request.args.get('part_num_relation_id')

    if not project_id or not part_num_relation_id:
        return jsonify({'success': False, 'message': '参数不对'})

    result = {
        'success': True,
        'level': 2,
        'data': []
    }

    part_number = ProjectPartNumber.query. \
        filter_by(project_id=project_id, part_num_relation_id=part_num_relation_id). \
        order_by(ProjectPartNumber.id).all()

    if not part_number:
        return jsonify(result)

    result['data'] = [v.to_dict() for v in part_number]

    return jsonify(result)


@main.route('/project/part/number/submit/<int:project_id>', methods=['POST'])
@login_required
def submit_part_number(project_id):
    part_num_relation_id = request.args.get('part_num_relation_id')
    if not part_num_relation_id:
        return jsonify({'success': False, 'message': '填写完整'})

    number = request.form.getlist('number')
    las = request.form.getlist('las')
    # las = sorted(las)
    number = [v for v in number if v]
    if not number:
        ProjectPartNumber.query.filter_by(project_id=project_id, part_num_relation_id=part_num_relation_id).delete()
        return jsonify({'success': True, 'message': '更新成功'})

    result = list()
    try:
        for index, n in enumerate(number):
            d = {
                'project_id': project_id,
                'part_num_relation_id': part_num_relation_id,
                'number': n,
                'las': las[index],
            }
            result.append(d)
    except KeyError:
        return jsonify({'success': False, 'message': '填写完整'})

    try:
        ProjectPartNumber.query.filter_by(project_id=project_id, part_num_relation_id=part_num_relation_id).delete()
    except:
        pass

    db_list = list()
    for r in result:
        db_list.append(ProjectPartNumber(**r))

    db.session.add_all(db_list)
    return jsonify({'success': True, 'message': '更新成功'})


# 第二个节点 操作符
@main.route('/part/number/tree/delete/<int:id>', methods=['POST'])
@login_required
def delete_part_number_tree(id):
    part_relation = ProjectPartNumRelation.query.filter_by(id=id).first()
    if not part_relation:
        return jsonify({'success': False, 'message': '没有此记录'})
    if not part_relation.parent_id:
        return jsonify({'success': False, 'message': '这节点为根节点，不支持删除'})

    db.session.delete(part_relation)
    return jsonify({'success': True, 'message': '更新成功'})


@main.route('/part/number/relation', methods=['POST'])
@login_required
def update_part_number_relation_order():
    id = request.args.get('id')

    type = request.args.get('type')
    if not id or not type:
        return jsonify({'success': False, 'message': '参数不对'})

    part_relation = ProjectPartNumRelation.query.filter_by(id=id).first()
    if not part_relation:
        return jsonify({'success': False, 'message': '没有记录'})
    parent_id = part_relation.parent_id

    if type == 'up':
        prev_part_relation = ProjectPartNumRelation.query. \
            filter_by(parent_id=parent_id, relation_order=part_relation.relation_order - 1).first()
        if not prev_part_relation:
            return jsonify({'success': False, 'message': '不能上移'})

        pre_order = prev_part_relation.relation_order + 1
        this_order = prev_part_relation.relation_order

        prev_part_relation.relation_order = pre_order
        part_relation.relation_order = this_order

        return jsonify({'success': True, 'message': '更新成功'})

    else:
        next_part_relation = ProjectPartNumRelation.query. \
            filter_by(parent_id=parent_id, relation_order=part_relation.relation_order + 1).first()
        if not next_part_relation:
            return jsonify({'success': False, 'message': '不能下移'})

        next_order = next_part_relation.relation_order - 1
        this_order = next_part_relation.relation_order

        next_part_relation.relation_order = next_order
        part_relation.relation_order = this_order

        return jsonify({'success': True, 'message': '更新成功'})


@main.route('/part/number/edit/name', methods=['POST'])
@login_required
def edit_part_number_name():
    name = request.form.get('name')
    id = request.form.get('id')
    if not name:
        return jsonify({'success': False, 'message': '名称不能为空'})

    part_relation = ProjectPartNumRelation.query.filter_by(id=id).first()

    if not part_relation:
        return jsonify({'success': False, 'message': '没有此记录'})

    part_relation.name = name
    db.session.add(part_relation)

    return jsonify({'success': True, 'message': '更新成功'})
