from .models import *
import os
from flask import make_response, current_app, send_file, abort


def get_copy_parent_id(copy_id):
    copy_parent_id = None
    if copy_id:
        product_info = ProjectRelation.query.filter_by(id=copy_id).first()
        copy_parent_id = product_info.parent_id
        if not copy_parent_id:
            return {'success': False, 'message': '第一个不能被复制'}

    return copy_parent_id


def get_copy_part_info(copy_id):
    if not copy_id:
        return

    info = ProjectPartNumRelation.query.filter_by(id=copy_id).first()
    return info


def delete_project_children(id):
    relations = ProjectRelation.query.filter_by(parent_id=id).all()
    if not relations:
        return

    for relation in relations:
        next_id = relation.id
        db.session.delete(relation)
        db.session.commit()

        delete_project_children(next_id)


def order_delete_project(parent_id):
    project_relations = ProjectRelation.query.filter_by(parent_id=parent_id). \
        order_by(ProjectRelation.relation_order, ProjectRelation.id).all()
    if not project_relations:
        return
    for index, val in enumerate(project_relations, start=1):
        val.relation_order = index
        db.session.add(val)


def copy_product_children(no_copy_id, copy_result_id):
    parent_id = copy_result_id[0]
    product_relation = ProjectRelation.query.filter_by(parent_id=no_copy_id).all()
    if not product_relation:
        return

    for v in product_relation:
        d = {
            'parent_id': parent_id,
            'project_id': v.project_id,
            'level': v.level,
        }
        copy_result_id = ProjectRelation.add_project_relation(d, v.name, v.project_id)
        if not copy_result_id:
            return
        copy_product_children(v.id, copy_result_id)


def get_func_relation(init_result, project_id, parent_id):
    if not project_id:
        return init_result

    project_relation = ProjectRelation.query.filter_by(id=parent_id).first()
    if not project_relation:
        return init_result

    init_result['nodedata'].append({'category': 'ProductNode',
                                    'name': project_relation.name,
                                    'type': 'project',
                                    'level': project_relation.level,
                                    'key': 'product_node_%s' % parent_id,
                                    'parent_id': parent_id,
                                    })
    # result = {
    #     'nodedata': [],
    #     'linkdata': [],
    # }
    func_relations = ProjectRelation.query.order_by(ProjectRelation.id.asc()). \
        filter_by(project_id=project_id, parent_id=parent_id, type='func').all()

    if not func_relations:
        return init_result

    for index, fr in enumerate(func_relations):
        init_result['nodedata'].append({
            'category': 'FuncNode',
            'name': fr.name,
            'key': fr.id,
            'level': fr.level,
            'parent_id': fr.parent_id,
        })
        init_result['linkdata'].append({
            'from': 'product_node_%s' % parent_id,
            'to': fr.id,
            'category': 'ProductLink'
        })

    return init_result


def get_project_children(project_id):
    result = list()
    first_relation = ProjectRelation.query.filter_by(project_id=project_id, level=1).first()
    d = {
        'level_1': first_relation.name,
    }

    second_relation = ProjectRelation.query.filter_by(parent_id=first_relation.id, level=2).all()
    if not second_relation:
        return result

    for v in second_relation:
        d['level_2'] = v.name

        third_relation = ProjectRelation.query.filter_by(parent_id=v.id, level=3).all()
        if third_relation:
            for th in third_relation:
                d['level_3'] = th.name
                d['level_3_id'] = th.id

                forth_relation = ProjectRelation.query.filter_by(parent_id=th.id, level=4).all()
                if forth_relation:
                    for forth in forth_relation:
                        # d['level_4'] = forth.name
                        # print(forth.name)
                        d.update({'level_4': forth.name, 'level_4_id': forth.id})
                        result.append(d.copy())

    return result


def get_project_children_v2(project_id, last_relation_id):
    result = list()
    first_relation = ProjectRelation.query.filter_by(project_id=project_id, level=1).first()
    d = {
        'level_1': first_relation.name,
    }

    second_relation = ProjectRelation.query.filter_by(parent_id=first_relation.id, level=2).all()
    if not second_relation:
        return result

    for v in second_relation:
        d['level_2'] = v.name
        d['level_2_id'] = v.id

        third_relation = ProjectRelation.query.filter_by(parent_id=v.id, level=3).all()
        if third_relation:
            for th in third_relation:
                d['level_3'] = th.name

                if th.id == last_relation_id:
                    forth_relation = ProjectRelation.query.filter_by(parent_id=th.id, level=4).all()
                    if forth_relation:
                        for forth in forth_relation:
                            d.update({'level_4': forth.name, 'level_4_id': forth.id})
                            result.append(d.copy())

    return result


def download_files(filename_path, filename):
    try:
        from urllib.parse import quote

        print(filename_path)

        response = make_response(send_file(filename_path, as_attachment=True))
        response.headers["Content-Disposition"] = \
            "attachment;" \
            "filename*=UTF-8''{utf_filename}".format(
                utf_filename=quote(filename.encode('utf-8'))
            )
        return response
    except Exception as e:
        print(e)
        abort(404)
