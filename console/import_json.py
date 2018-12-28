# coding: utf-8
from .app import db
from .app.main.models import ProjectRelation, AttrContent, ProjectData, ProjectPartNumber, ProjectPartNumRelation, \
    ProjectPartNumberAttr
from .app.manage.models import ExtraAttrData
from .app.models import Modification
import json


class ImportJson(object):

    def __init__(self, name, project_id, project_relation, part_relation, now):
        self.name = name
        self.project_id = project_id
        self.project_relation = project_relation

        self.part_relation = part_relation

        self.now = now
        self.default_conf = dict()
        self.content = {
            'ext_conf_data': dict(),
            'conf_data': dict(),
        }

    def set_project_relation_one(self):
        pr_parent = self.project_relation.copy()
        pr_one_child = pr_parent['child']

        attr = pr_parent['attr']
        if attr.get('real_content'):
            attr_content = json.loads(attr['real_content'])
            if attr_content.get('ConfigurationFileNumber'):
                attr_content['ConfigurationFileNumber'] = '{}_{}'.format(attr_content['ConfigurationFileNumber'],
                                                                         self.now)
            attr['real_content'] = json.dumps(attr_content)
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

                    default_conf = c.get('default_conf')
                    conf_data = c.get('conf_data')
                    ext_conf_data = c.get('ext_conf_data')

                    err_pass(c)
                    err_ext(c)
                    if c.get('id'):
                        del c['id']

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

                    if default_conf:
                        self.default_conf[new_data.id] = default_conf
                    if conf_data:
                        self.content['conf_data'][new_data.id] = conf_data
                    if ext_conf_data:
                        self.content['ext_conf_data'][new_data.id] = ext_conf_data

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

    def set_modification(self):
        if not self.default_conf:
            return
        d = {
            'project_id': self.project_id,
            'default_conf': json.dumps(self.default_conf),
            'content': json.dumps(self.content),
        }
        print(self.default_conf)
        print(self.content)
        db.session.add(Modification(**d))
        db.session.commit()

    def set_part_num_relation(self):
        part_relation = self.part_relation
        if not part_relation:
            return
        part_relation_child = part_relation.get('child')
        del part_relation['child']

        part_relation['project_id'] = self.project_id
        part_relation_db = ProjectPartNumRelation(**part_relation)
        db.session.add(part_relation_db)
        db.session.flush()

        part_num_relation_id = part_relation_db.id
        if not part_relation_child:
            return

        result_attr = list()
        result_part = list()
        for pr in part_relation_child:
            pr_part = pr.get('part')
            attr = pr.get('attr')
            pr['parent_id'] = part_num_relation_id
            pr['project_id'] = self.project_id

            del pr['part']
            del pr['attr']

            result_relation = ProjectPartNumRelation(**pr)
            db.session.add(result_relation)
            db.session.flush()
            if attr:
                attr['project_id'] = self.project_id
                attr['part_num_relation_id'] = result_relation.id
                result_attr.append(ProjectPartNumberAttr(**attr))

            if pr_part:
                for pp in pr_part:
                    pp['project_id'] = self.project_id
                    pp['part_num_relation_id'] = result_relation.id
                    result_part.append(ProjectPartNumber(**pp))

        db.session.add_all(result_attr)
        db.session.add_all(result_part)
        db.session.commit()

    def run(self):
        if not self.project_relation:
            return

        pr_one_child, pr_one_id = self.set_project_relation_one()
        self.set_project_relation_other(pr_one_child, pr_one_id)

        self.set_modification()

        self.set_part_num_relation()


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


def err_ext(c):
    try:
        del c['default_conf']
    except KeyError:
        pass
    try:
        del c['conf_data']
    except KeyError:
        pass
    try:
        del c['ext_conf_data']
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
