import xml.dom.minidom
import os
import json
from app import create_app
from app.main.models import Project, ProjectRelation, ProjectData
from app.manage.models import AttrContent
from app.main.func import get_project_children
from collections import defaultdict

app = create_app()
app.app_context().push()


class ExportXml(object):

    def __init__(self, project_id):
        self.project_id = project_id

    def set_path(self):
        path = os.path.abspath(os.path.dirname(__file__))
        real_path = os.path.join(path, 'files')
        files_path = os.path.join(real_path, '%s.xml' % self.xml_managers_attr)

        if not os.path.exists(real_path):
            os.makedirs(real_path)
        return files_path

    @property
    def xml_managers_attr(self):
        project = Project.query.get_or_404(self.project_id)
        return project.name

    @property
    def xml_header_attr(self):
        result = dict()
        project_relation = ProjectRelation.query.filter_by(project_id=self.project_id, parent_id=None).first()
        attr_content = AttrContent.query.filter_by(project_relation_id=project_relation.id).first()

        if not attr_content or not attr_content.real_content:
            return result

        content = json.loads(attr_content.real_content)
        return content

    @property
    def read_section(self):
        result = get_project_children(self.project_id)
        return list(set([v['level_2'] for v in result if v.get('level_2')]))

    @property
    def modification(self):
        r = defaultdict(list)
        result = get_project_children(self.project_id)
        for v in result:
            r[v['level_2']].append({'project_relation_id': v['level_4_id']})

        new_result = dict()
        for address, projects in r.items():
            for project in projects:
                pass

            project = ProjectData.query.filter_by(project_id=self.project_id).all()
            d = {
                'conf_data': [(v.conf_data, v.las) for v in project if v.conf_data]
            }
            new_result[address] = d

        print(new_result)
        return new_result

    def set_xml(self):
        doc = xml.dom.minidom.Document()
        root = doc.createElement('ConfigurationModule')

        root.setAttribute('%s-CONFIG-SCHEMA-VERSION' % self.xml_managers_attr, '1.0')
        doc.appendChild(root)

        manager_dict = self.xml_header_attr
        header_manager = doc.createElement('Header')
        if manager_dict:
            for key, val in manager_dict.items():
                node_name = doc.createElement(key)
                node_name.appendChild(doc.createTextNode(str(val)))
                header_manager.appendChild(node_name)
        root.appendChild(header_manager)

        section_manager = doc.createElement('ReadSection')
        if self.read_section:
            for v in self.read_section:
                node_name = doc.createElement('ReadItem')
                node_name.setAttribute('IDREF', v)
                section_manager.appendChild(node_name)
        root.appendChild(section_manager)

        modification_section = self.modification
        node_modification = doc.createElement('ModificationSection')
        if modification_section:
            for key, val in modification_section.items():
                node_modification_item = doc.createElement('ModificationItem')
                node_modification_item.setAttribute('IDREF', key)

                node_conf_data = doc.createElement('ConfData')
                node_conf_data.setAttribute('useConfData', 'true')
                for data in val['conf_data']:
                    node_config_data = doc.createElement('ConfigData')
                    node_config_data.setAttribute('Value', data[0])
                    node_config_data.setAttribute('ConfigExpression', data[1])
                    node_conf_data.appendChild(node_config_data)

                node_modification_item.appendChild(node_conf_data)

                node_modification.appendChild(node_modification_item)

        root.appendChild(node_modification)

        return doc

    def run(self):
        files_path = self.set_path()
        doc = self.set_xml()
        fp = open(files_path, 'w', encoding='utf-8')
        doc.writexml(fp, indent='\t', addindent='\t', newl='\n', encoding="utf-8")


if __name__ == '__main__':
    export_xml = ExportXml(1)
    export_xml.run()
