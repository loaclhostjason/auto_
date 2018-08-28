# coding: utf-8
from .app import db
from .app.main.models import ProjectRelation, AttrContent, ProjectData
from .app.manage.models import ExtraAttrData


class ImportJson(object):

    def __init__(self, name, project_id, project_relation):
        self.name = name
        self.project_id = project_id
        self.project_relation = project_relation

    def set_project_relation_one(self):
        pr_parent = self.project_relation.copy()
        pr_one_child = pr_parent['child']

        attr = pr_parent['attr']
        extra_attr = pr_parent['extra_attr']
        del pr_parent['attr']
        del pr_parent['extra_attr']
        del pr_parent['child']

        pr_parent['project_id'] = self.project_id
        pr_parent['name'] = self.name
        new_pr_parent = ProjectRelation(**pr_parent)
        db.session.add(new_pr_parent)
        db.session.flush()

        self.set_attr(attr, new_pr_parent.id)
        self.set_extra_attr(extra_attr, new_pr_parent.id)
        return pr_one_child, new_pr_parent.id

    def set_project_relation_other(self, child_data, init_parent_id=None):
        if child_data:
            for c in child_data:
                if not c.get('project_data'):
                    attr_info, ext_attr_info = get_attr(c)

                    err_pass(c)

                    try:
                        pr_child = c['child']
                    except KeyError:
                        pr_child = None

                    try:
                        del c['child']
                    except KeyError:
                        pass

                    c['parent_id'] = init_parent_id
                    c['project_id'] = self.project_id

                    new_data = ProjectRelation(**c)
                    db.session.add(new_data)
                    db.session.flush()

                    self.set_attr(attr_info, new_data.id)
                    self.set_extra_attr(ext_attr_info, new_data.id)

                    self.set_project_relation_other(pr_child, new_data.id)
                else:
                    self.set_project_data(c['project_data'], init_parent_id)

    def set_attr(self, attr_info, id):
        if attr_info:
            attr_info['project_relation_id'] = id
            attr_info['project_id'] = self.project_id
            db.session.add(AttrContent(**attr_info))
            db.session.commit()

    def set_extra_attr(self, ext_attr_info, id):
        if ext_attr_info:
            ext_attr_info['project_relation_id'] = id
            ext_attr_info['project_id'] = self.project_id
            db.session.add(ExtraAttrData(**ext_attr_info))
            db.session.commit()

    def set_project_data(self, project_data, relation_id):
        if project_data and relation_id:
            project_data['project_relation_id'] = relation_id
            project_data['project_id'] = self.project_id
            err_pass(project_data)
            db.session.add(ProjectData(**project_data))
            db.session.commit()

    def run(self):
        if not self.project_relation:
            return

        pr_one_child, pr_one_id = self.set_project_relation_one()
        self.set_project_relation_other(pr_one_child, pr_one_id)


'''
extra func 
'''


def err_pass(c):
    try:
        del c['attr']
    except KeyError:
        pass
    try:
        del c['extra_attr']
    except KeyError:
        pass


def get_attr(c):
    try:
        attr_info = c['attr']
    except KeyError:
        attr_info = None
    try:
        ext_attr_info = c['extra_attr']
    except KeyError:
        ext_attr_info = None

    return attr_info, ext_attr_info
