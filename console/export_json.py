# coding: utf-8
import json
import os
from .app import create_app
from .app.main.models import Project, ProjectRelation, ProjectData, AttrContent, ProjectPartNumRelation, \
    ProjectPartNumber, ProjectPartNumberAttr
from .app.manage.models import ExtraAttrData
from .app.models import Modification
from console.config import Config
from collections import defaultdict

app = create_app()
app.app_context().push()


class ExportJson(object):
    def __init__(self, project_id):
        self.project_id = project_id
        self.project = Project.query.filter_by(id=project_id).first()

        self.file_path = Config.JSON_FILE_PATH

        self.pr_result = defaultdict(list)
        self.default_conf = dict()
        self.content = {
            'ext_conf_data': dict(),
            'conf_data': dict(),
        }

    @property
    def file_name(self):
        project = self.project
        if not project:
            return
        filename = '[{}]{}_{}.json'.format(project.id, project.project_group.name, project.name)
        return filename

    def get_project(self):
        return self.project.to_json() if self.project else None

    def get_project_relation_children(self):
        # old
        old_default_conf = self.get_mod_default_conf()
        ext_conf_data, conf_data = self.get_mod_content()

        result = list()
        first_relation = ProjectRelation.query.filter_by(project_id=self.project_id, level=1).first()
        fr_json = first_relation.to_json(remove_key=['id'])
        fr_json['attr'] = self.get_attr(first_relation.id)
        fr_json['extra_attr'] = self.get_extra_attr(first_relation.id)
        d = {
            'project_relation': fr_json,
        }

        second_relation = ProjectRelation.query.filter_by(parent_id=first_relation.id, level=2).all()
        if not second_relation:
            return d

        for v in second_relation:
            sec_json = v.to_json(remove_key=['id'])
            sec_json['attr'] = self.get_attr(v.id)
            sec_json['extra_attr'] = self.get_extra_attr(v.id)
            fr_json['child'].append(sec_json)

            third_relation = ProjectRelation.query.filter_by(parent_id=v.id, level=3).all()
            if third_relation:
                for th in third_relation:
                    third_json = th.to_json(remove_key=['id'])
                    third_json['attr'] = self.get_attr(th.id)
                    third_json['default_conf'] = old_default_conf.get(str(th.id))
                    third_json['conf_data'] = conf_data.get(str(th.id))
                    third_json['ext_conf_data'] = ext_conf_data.get(str(th.id))

                    sec_json['child'].append(third_json)

                    forth_relation = ProjectRelation.query.filter_by(parent_id=th.id, level=4).all()
                    if forth_relation:
                        for forth in forth_relation:
                            forth_json = forth.to_json(remove_key=['id'])
                            third_json['child'].append(forth_json)

                            project_data = ProjectData.query.filter_by(project_relation_id=forth.id).all()
                            if project_data:
                                real_dict = {
                                    'project_data': None
                                }
                                for pd in project_data:
                                    real_dict['project_data'] = pd.to_json(remove_key=['id'])

                                forth_json['child'].append(real_dict)
                            result.append(d.copy())
        return d

    def get_project_relation(self):
        project_relation = self.get_project_relation_children()

        return project_relation

    def create_json(self, data):
        file_name = os.path.join(self.file_path, self.file_name)
        with open(file_name, 'w') as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def get_attr(project_relation_id):
        attr_content = AttrContent.query.filter_by(project_relation_id=project_relation_id).first()
        if not attr_content:
            return

        attr_content = attr_content.to_json(remove_key=['id']) if attr_content else None
        return attr_content

    @staticmethod
    def get_extra_attr(project_relation_id):
        extra_data = ExtraAttrData.query.filter_by(project_relation_id=project_relation_id).first()
        if not extra_data:
            return

        extra_data = extra_data.to_json(remove_key=['id']) if extra_data else None
        return extra_data

    def __get_modification(self):
        modification = Modification.query.filter_by(project_id=self.project_id).first()
        if not modification:
            return None, None

        default_conf = json.loads(modification.default_conf or '{}')
        content = json.loads(modification.content or '{}')
        return default_conf, content

    def get_mod_default_conf(self):
        result, *args = self.__get_modification()
        return result

    def get_mod_content(self):
        *args, result = self.__get_modification()
        if not result:
            return dict(), dict()
        return result['ext_conf_data'], result['conf_data']

    def get_part_attr(self, part_num_relation_id):
        part_attr = ProjectPartNumberAttr.query. \
            filter_by(project_id=self.project_id, part_num_relation_id=part_num_relation_id).first()
        if not part_attr:
            return
        result = part_attr.to_json()
        return result

    def get_part_number(self, part_num_relation_id):
        part_number = ProjectPartNumber.query.order_by(ProjectPartNumber.id). \
            filter_by(project_id=self.project_id, part_num_relation_id=part_num_relation_id).all()
        if not part_number:
            return
        result = list()
        for pn in part_number:
            result.append(pn.to_json())
        return result

    def get_part_relation(self):
        part_relation = ProjectPartNumRelation.query.filter_by(project_id=self.project_id, level=1).first()
        if not part_relation:
            return
        result = part_relation.to_json(remove_key=['id', 'part', 'attr'])
        part_all = ProjectPartNumRelation.query.filter_by(parent_id=part_relation.id). \
            order_by(ProjectPartNumRelation.relation_order, ProjectPartNumRelation.id).all()
        if not part_all:
            return result
        for pa in part_all:
            pa_attr = self.get_part_attr(pa.id)
            pa_number = self.get_part_number(pa.id)
            pa_data = pa.to_json(remove_key=['id', 'child'])
            pa_data['attr'] = pa_attr
            pa_data['part'] = pa_number
            result['child'].append(pa_data)
        return result

    def run(self):
        if not self.get_project():
            return
        # project
        project = self.get_project()

        # project relation
        project_relation = self.get_project_relation()

        # get_part_relation
        part_relation = self.get_part_relation()
        # print(part_relation)

        data = {
            'project': project,
            'project_relation': project_relation['project_relation'],
            'part_relation': part_relation,
        }
        self.create_json(data)
