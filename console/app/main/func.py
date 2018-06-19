from .models import *


def get_copy_parent_id(copy_id):
    copy_parent_id = None
    if copy_id:
        product_info = ProjectRelation.query.filter_by(id=copy_id).first()
        copy_parent_id = product_info.parent_id
        if not copy_parent_id:
            return {'success': False, 'message': '第一个不能被复制'}

    return copy_parent_id


def delete_product_children(id):
    relations = ProjectRelation.query.filter_by(parent_id=id).all()
    if not relations:
        return

    for relation in relations:
        next_id = relation.id
        db.session.delete(relation)
        db.session.commit()

        delete_product_children(next_id)


def copy_product_children(no_copy_id, copy_result_id):
    parent_id = copy_result_id[0]
    product_relation = ProjectRelation.query.filter_by(parent_id=no_copy_id).all()
    if not product_relation:
        return

    for v in product_relation:
        d = {
            'parent_id': parent_id,
            'product_id': v.product_id,
            'level': int(v.level),
        }
        copy_result_id = ProjectRelation.add_project_relation(d, v.name, v.project_id)
        if not copy_result_id:
            return
        copy_product_children(v.id, copy_result_id)