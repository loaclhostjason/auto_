from . import main
from flask import jsonify, request
from flask_login import login_required, current_user
from .models import *
from .func import *


# project tree
@main.route('/project/tree')
@login_required
def get_project_tree():
    result = {
        'nodedata': [],
        'linkdata': [],
    }

    project_id = request.args.get('project_id')
    if not project_id:
        return jsonify({'success': False, 'message': '没有获取到配置文件信息'})

    project_relations = ProjectRelation.query.filter_by(project_id=project_id).order_by(ProjectRelation.relation_order,
                                                                                        ProjectRelation.id).all()
    if not project_relations:
        return jsonify({'success': True, 'data': result})

    link_data = []
    for relation in project_relations:
        if relation.parent_id:
            link_data.append({'from': relation.parent_id, 'to': relation.id})

        result['nodedata'].append({
            'name': relation.name,
            'key': relation.id,
            'level': relation.level,
        })

    result['linkdata'] = link_data
    return jsonify({'success': True, 'data': result})


# project edit
@main.route('/project/create', methods=['POST'])
@login_required
def create_project():
    form_data = request.form.to_dict()
    if not form_data.get('name'):
        return jsonify({'success': False, 'message': '项目名称不能为空'})

    project = Project.query.filter_by(name=form_data['name']).first()
    if project:
        return jsonify({'success': False, 'message': '项目名称重复'})

    d = {
        'name': form_data['name'],
        'user_id': current_user.get_id(),
    }

    add_project = Project(**d)
    db.session.add(add_project)
    db.session.flush()

    project_id = add_project.id

    project_relation = {
        'name': form_data['name'],
        'project_id': project_id
    }

    relation = ProjectRelation(**project_relation)
    db.session.add(relation)
    return jsonify({'success': True, 'message': '更新成功', 'project_id': project_id})


@main.route('/project/content/add/<int:id>', methods=['POST'])
@login_required
def add_file_tree_content(id):
    form_data = request.form.to_dict()
    copy_id = request.args.get('copy_id')
    action = request.args.get('action')

    copy_parent_id = get_copy_parent_id(copy_id)
    if isinstance(copy_parent_id, dict):
        return jsonify(copy_parent_id)

    if not form_data.get('content'):
        return jsonify({'success': False, 'message': '内容不能为空'})

    d = {
        'parent_id': form_data.get('parent_id') if not copy_parent_id else copy_parent_id,
        'project_id': id,
        'level': form_data.get('level'),
    }

    copy_result_id = ProjectRelation.add_project_relation(d, form_data['content'], id)
    if copy_result_id and action == 'copy':
        copy_product_children(key, copy_result_id)
    return jsonify({'success': True, 'type': form_data.get('type')})


@main.route('/project/tree/delete/<int:id>', methods=['POST'])
@login_required
def delete_project(id):
    project_relation = ProjectRelation.query.filter_by(id=id).first()
    if not project_relation:
        return jsonify({'success': False, 'message': '没有此记录'})
    if not project_relation.parent_id:
        return jsonify({'success': False, 'message': '这节点为根节点，不支持删除'})
    db.session.delete(project_relation)
    delete_product_children(id)
    return jsonify({'success': True, 'message': '更新成功'})
