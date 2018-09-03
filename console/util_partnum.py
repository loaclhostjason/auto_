import json
import sys
import os
from .config import Config
from .app.main.models import Project
from console.dom import minidom

os_name = sys.platform
operate = '\n' if os_name.startswith('win') else '\r\n'


class UtilPartNum(object):
    def __init__(self, project_id):
        self.project_id = project_id

    @property
    def project_info(self):
        project = Project.query.filter_by(id=self.project_id).first()
        return project

    def set_path(self):
        project = self.project_info
        if not project:
            return
        real_path = Config.PART_PATH_ROOT
        files_path = os.path.join(real_path,
                                  '{}_{}_partnum.xml'.format(project.project_group.name.lower(), project.name.lower()))
        return files_path

    def set_xml(self):
        doc = minidom.Document()
        root = doc.createElement('ConfigurationModule')

        root.setAttribute('VERSION', '1.0')
        doc.appendChild(root)

        return doc

    def run(self):
        files_path = self.set_path()
        if not files_path:
            return

        doc = self.set_xml()
        with open(files_path, 'w', encoding='utf-8') as f:
            doc.writexml(f, indent='', addindent='  ', newl=operate, encoding="utf-8")

        file_data = ""
        with open(files_path, 'r', encoding='UTF-8') as f:
            for line in f:
                file_data += line[:-1] + operate

        with open(files_path, 'w', encoding='utf-8') as f:
            f.write(file_data)
