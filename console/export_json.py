# coding: utf-8
import json
import os
from .app import create_app
from .app.main.models import Project, ProjectRelation, ProjectData
from console.config import Config

app = create_app()
app.app_context().push()


class ExportJson(object):
    def __init__(self, project_id):
        self.project = Project.query.filter_by(id=project_id).first()

        self.file_path = Config.JSON_FILE_PATH

    @property
    def file_name(self):
        project = self.project
        if not project:
            return
        filename = '[{}]{}_{}.json'.format(project.id, project.project_group.name, project.name)
        return filename

    def get_project(self):
        return self.project.to_json() if self.project else None

    def create_json(self, data):
        file_name = os.path.join(self.file_path, self.file_name)
        with open(file_name, 'w') as f:
            json.dump(data, f, indent=4)

    def run(self):
        if not self.get_project():
            return

        data = {
            'project': self.get_project(),
            'project_data': None,
            'attr_content': None,
        }
        self.create_json(data)
