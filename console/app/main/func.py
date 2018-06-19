from .models import *


def get_copy_parent_id(copy_id):
    copy_parent_id = None
    if copy_id:
        product_info = ProjectRelation.query.filter_by(id=copy_id).first()
        copy_parent_id = product_info.parent_id
        if not copy_parent_id:
            return {'success': False, 'message': '第一个不能被复制'}

    return copy_parent_id


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
