import xml.dom.minidom
import os
import json
from app import create_app
from app.main.models import Project, ProjectRelation, ProjectData
from app.manage.models import AttrContent
from app.main.func import get_project_children
from collections import defaultdict
from enum import Enum

app = create_app()
app.app_context().push()


class Byte(Enum):
    byte = 'BytePosition'


class Bite(Enum):
    bite = 'BitPosition'


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
    def xml_did_list(self):
        result = dict()
        project_relation = ProjectRelation.query.filter_by(project_id=self.project_id, level=2).all()
        if not project_relation:
            return result

        for pr in project_relation:
            attr_content = AttrContent.query.filter_by(project_relation_id=pr.id).first()
            real_content = json.loads(attr_content.real_content) if attr_content and attr_content.real_content else None
            result[pr.name] = real_content or {}

        return result

    @property
    def read_section(self):
        result = get_project_children(self.project_id)
        return list(set([v['level_2'] for v in result if v.get('level_2')]))

    def __get_(self, projects):
        d = defaultdict(list)
        for project in projects:
            p = ProjectData.query.filter_by(project_id=self.project_id).filter_by(project_relation_id=project['project_relation_id']).first()
            content = json.loads(p.content) if p and p.content else None
            d['parameter_name'] = p.name if p else 'null'

            if content:
                for v in ['byte0', 'byte1', 'byte2', 'byte3']:
                    if content.get(v):

                        d['byte'].append({'BytePosition': content.get(v)})

                        for bit in ['bit0_', 'bit1_', 'bit2_', 'bit3_']:
                            for index in range(8):
                                if content.get('%s%d' % (bit, index)):
                                    d['byte'].append({'BitPosition': index})
        return d

    @property
    def modification(self):
        r = defaultdict(list)
        result = get_project_children(self.project_id)
        for v in result:
            r[v['level_2']].append({'project_relation_id': v['level_4_id']})

        new_result = dict()
        for address, projects in r.items():
            project_query = ProjectData.query.filter_by(project_id=self.project_id)
            project = project_query.all()
            d = {
                'conf_data': [(v.conf_data, v.las) for v in project if v.conf_data]
            }
            new_result[address] = self.__get_(projects)
            new_result[address]['conf_data'] = d['conf_data']

        print(11, new_result)
        return new_result

    def set_xml(self):
        doc = xml.dom.minidom.Document()
        root = doc.createElement('ConfigurationModule')

        root.setAttribute('%s-CONFIG-SCHEMA-VERSION' % self.xml_managers_attr, '1.0')
        doc.appendChild(root)

        # header
        manager_dict = self.xml_header_attr
        header_manager = doc.createElement('Header')
        if manager_dict:
            for key, val in manager_dict.items():
                node_name = doc.createElement(key)
                node_name.appendChild(doc.createTextNode(str(val)))
                header_manager.appendChild(node_name)
        root.appendChild(header_manager)

        # did list
        did_list = {k: v for k, v in self.xml_did_list.items() if v}
        node_did_list = doc.createElement('DidList')
        if did_list:
            for cid, val in did_list.items():
                node_did_item = doc.createElement('DidItem')
                for k, v in val.items():
                    did_item_s = doc.createElement(k)
                    did_item_s.appendChild(doc.createTextNode(str(v)))
                    node_did_item.appendChild(did_item_s)
                node_did_list.appendChild(node_did_item)
        root.appendChild(node_did_list)

        # ReadSection
        section_manager = doc.createElement('ReadSection')
        if self.read_section:
            for v in self.read_section:
                node_name = doc.createElement('ReadItem')
                node_name.setAttribute('IDREF', v)
                section_manager.appendChild(node_name)
        root.appendChild(section_manager)

        # ModificationSection
        modification_section = self.modification
        node_modification = doc.createElement('ModificationSection')
        if modification_section:
            for key, val in modification_section.items():
                node_modification_item = doc.createElement('ModificationItem')
                node_modification_item.setAttribute('IDREF', key)

                # Parameter
                node_parameter = doc.createElement('Parameter')
                node_parameter.setAttribute('ParamDefaultValue', val['conf_data'][0][0] if val['conf_data'] else '')

                # ParameterName
                node_parameter_name = doc.createElement('ParameterName')
                node_parameter_name.appendChild(doc.createTextNode(str(val['parameter_name'])))
                node_modification_item.appendChild(node_parameter_name)

                # bite
                if val['byte']:
                    for v in val['byte']:
                        for k, v in v.items():
                            node_byte_name = doc.createElement(k)
                            node_byte_name.appendChild(doc.createTextNode(str(v)))
                            node_modification_item.appendChild(node_byte_name)

                # ConfData
                node_conf_data = doc.createElement('ConfData')
                node_conf_data.setAttribute('useConfData', 'true')
                for data in val['conf_data']:
                    node_config_data = doc.createElement('ConfigData')
                    node_config_data.setAttribute('Value', data[0])
                    node_config_data.setAttribute('ConfigExpression', data[1])
                    node_conf_data.appendChild(node_config_data)

                    node_parameter.appendChild(node_conf_data)

                node_modification_item.appendChild(node_parameter)
                node_modification.appendChild(node_modification_item)
        root.appendChild(node_modification)

        node_write_section = doc.createElement('WriteSection')
        if modification_section:
            for key, val in modification_section.items():
                node_write_item = doc.createElement('WriteItem')
                node_write_item.setAttribute('IDREF', key)
                node_write_item.setAttribute('DidWriteScope', 'All')
                node_write_item.setAttribute('DelayForMS', '0')
                node_write_section.appendChild(node_write_item)
        root.appendChild(node_write_section)

        return doc

    def run(self):
        files_path = self.set_path()
        doc = self.set_xml()
        fp = open(files_path, 'w', encoding='utf-8')
        doc.writexml(fp, indent='\t', addindent='\t', newl='\n', encoding="utf-8")


if __name__ == '__main__':
    export_xml = ExportXml(2)
    export_xml.run()
