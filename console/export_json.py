# coding: utf-8
import json
import os
from .app import create_app
from .app.main.models import Project, ProjectRelation, ProjectData
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

    @property
    def file_name(self):
        project = self.project
        if not project:
            return
        filename = '[{}]{}_{}.json'.format(project.id, project.project_group.name, project.name)
        return filename

    def get_project(self):
        return self.project.to_json() if self.project else None

    def __project_relation_children(self, project_relation):
        if project_relation:
            for pr_info in project_relation:
                children = ProjectRelation.query.filter_by(parent_id=pr_info.id).all()
                self.pr_result[pr_info.parent_id].append(pr_info.to_json())
                for v in self.pr_result.values():
                    for val in v:
                        if val['id'] == pr_info.parent_id:
                            val['info'] = pr_info.to_json()

                self.__project_relation_children(children)

    def get_project_relation(self):
        project_relation = ProjectRelation.query.filter_by(project_id=self.project_id, parent_id=None).all()

        if project_relation:
            self.__project_relation_children(project_relation)
        print(self.pr_result)

        project_relations = self.project.project_relation
        project_relation = [info.to_json() for info in project_relations if info]

        self.pr_result = []

        return project_relation

    def create_json(self, data):
        file_name = os.path.join(self.file_path, self.file_name)
        with open(file_name, 'w') as f:
            json.dump(data, f, indent=4)

    def run(self):
        if not self.get_project():
            return
        # project
        project = self.get_project()

        # project relation
        project_relation = self.get_project_relation()

        data = {
            'project': project,
            'project_relation': project_relation,
            'project_data': None,
            'attr_content': None,
        }
        self.create_json(data)
