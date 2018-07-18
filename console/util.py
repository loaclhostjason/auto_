import xml.dom.minidom
import os
import json
from app import create_app
from app.main.models import Project, ProjectRelation, ProjectData
from app.manage.models import AttrContent, Attr
from collections import defaultdict, OrderedDict
from enum import Enum
import datetime

app = create_app()
app.app_context().push()


class Byte(Enum):
    byte = 'BytePosition'


class Bite(Enum):
    bite = 'BitPosition'


class ExportXml(object):

    def __init__(self, project_id):
        self.project_id = project_id

        self.header_order = ['ApplicationLayer', 'PhysicalLayer']

    def set_path(self):
        path = os.path.abspath(os.path.dirname(__file__))
        real_path = os.path.join(path, 'files', 'all')
        files_path = os.path.join(real_path, '%s.xml' % self.xml_managers_attr)

        if not os.path.exists(real_path):
            os.makedirs(real_path)
        return files_path

    def set_dir_path(self, project_name):
        path = os.path.abspath(os.path.dirname(__file__))
        real_path = os.path.join(path, 'files', project_name)
        files_path = os.path.join(real_path, '%s.xml' % self.xml_managers_attr)

        if not os.path.exists(real_path):
            os.makedirs(real_path)
        return files_path

    @property
    def xml_managers_attr(self):
        project = Project.query.get_or_404(self.project_id)
        return project.name

    @staticmethod
    def __ecu_order():
        attr = Attr.query.filter_by(level=1).first()
        if not attr or not attr.content:
            return list()
        content = json.loads(attr.content)
        result = list()
        for c in content:
            if c.get('item_protocol'):
                result.append('%s-%s' % (c['item_protocol'], c['item']))
            else:
                result.append(c['item'])
        return result

    @property
    def xml_header_attr(self):
        result = OrderedDict()
        project_relation = ProjectRelation.query.filter_by(project_id=self.project_id, parent_id=None).first()

        if not project_relation:
            return result

        attr_content = AttrContent.query.filter_by(project_relation_id=project_relation.id).first()

        if not attr_content or not attr_content.real_content:
            return result

        content = json.loads(attr_content.real_content)

        order_content = self.__ecu_order()
        if order_content:
            for oc in order_content:
                result[oc] = content.get(oc)

        result_list = [(key, val) for key, val in result.items()]
        return result_list, dict(result)

    @property
    def xml_did_list(self):
        result = dict()
        project_relation = ProjectRelation.query.filter_by(project_id=self.project_id, level=2). \
            order_by(ProjectRelation.relation_order).all()
        if not project_relation:
            return result

        for pr in project_relation:
            attr_content = AttrContent.query.filter_by(project_relation_id=pr.id).first()
            real_content = json.loads(attr_content.real_content) if attr_content and attr_content.real_content else {}
            result[pr.name] = real_content or {}

        return result

    @property
    def __did_order(self):
        attr = Attr.query.filter_by(level=2).first()
        if not attr or not attr.content:
            return []
        content = json.loads(attr.content)
        result = list()
        for v in content:
            result.append(v['item'])
        return result

    @property
    def read_section(self):
        attr_content = AttrContent.query.filter_by(project_id=self.project_id).all()
        result = list()
        if attr_content:
            for ac in attr_content:
                real_content = json.loads(ac.real_content) if ac.real_content else None
                if real_content:
                    for key, val in real_content.items():
                        if key == 'DidNo':
                            result.append(val)
        return result

    def __get_(self, projects):
        d = defaultdict(list)

        project_relation_ids = [project['project_relation_id'] for project in projects if
                                project.get('project_relation_id')]

        attr_content = AttrContent.query.filter(AttrContent.project_relation_id.in_(project_relation_ids)).all()
        pro = ProjectRelation.query.filter(ProjectRelation.id.in_(project_relation_ids)).all()

        r = defaultdict(list)
        d['parameter_name'] = [{p.id: p.name} for p in pro]
        if attr_content:
            for ac in attr_content:
                content = json.loads(ac.real_content) if ac and ac.real_content else None
                if content:
                    r[ac.project_relation_id].append(content)
        d['byte'] = r
        return d

    @staticmethod
    def __parameter_order():
        return ['ParameterName', 'BytePosition', 'BitPosition', 'BitLength']

    @property
    def modification(self):
        did = self.read_section
        r = defaultdict(list)
        if did:
            for v in did:
                project_relation = ProjectRelation.query.filter_by(name=v).first()
                if project_relation:
                    project_relation_child = ProjectRelation.query.filter_by(parent_id=project_relation.id).all()
                    if project_relation_child:
                        for pc in project_relation_child:
                            r[v].append({'project_relation_id': pc.id})

        new_result = dict()

        if r:
            for address, projects in r.items():
                project_query = ProjectData.query.filter_by(project_id=self.project_id).order_by(ProjectData.id.desc())
                project = project_query.all()
                conf_data = defaultdict(list)
                for pro in project:
                    parent_relation = ProjectRelation.query.get_or_404(pro.project_relation_id)
                    conf_data[parent_relation.parent_id].append((pro.conf_data, pro.las))

                conf_data = {k: v for k, v in conf_data.items()}
                conf_data = {
                    'conf_data': conf_data
                }
                new_result[address] = dict(conf_data, **self.__get_(projects))

        return new_result

    def set_xml(self):
        doc = xml.dom.minidom.Document()
        root = doc.createElement('ConfigurationModule')

        root.setAttribute('%s-CONFIG-SCHEMA-VERSION' % self.xml_managers_attr, '1.0')
        doc.appendChild(root)

        # header
        manager_list, manager_dict = self.xml_header_attr
        header_manager = doc.createElement('Header')
        if manager_dict:
            protocols = [{v[0].split('-')[0]: [v[0].split('-')[1], v[1]]} for v in manager_list if '-' in v[0]]
            order_protocols_list = [v[0].split('-')[0] for v in manager_list if '-' in v[0]]
            order_protocols = list(set(order_protocols_list))
            order_protocols.sort(key=order_protocols_list.index)

            new_protocols = defaultdict(list)
            for pt in protocols:
                for kkk, vvv in pt.items():
                    new_protocols[kkk].append(vvv)

            node_name_protocol = doc.createElement('Protocol')
            inter_val = True
            for value in manager_list:
                if '-' in value[0] and inter_val:
                    inter_val = False
                    for nk in order_protocols:
                        node_protocol_k = doc.createElement(nk)
                        nv = new_protocols.get(nk) or []

                        if nv:
                            for nvv in nv:
                                node_protocol_k_name = doc.createElement(nvv[0])
                                node_protocol_k_name.appendChild(doc.createTextNode(str(nvv[1])))
                                node_protocol_k.appendChild(node_protocol_k_name)
                        if nk == 'PhysicalLayer':
                            node_pin1 = doc.createElement('Pin')
                            node_pin1.setAttribute('PinDefinition', 'CAN_H')
                            node_pin1.setAttribute('PinNumber', '6')
                            node_protocol_k.appendChild(node_pin1)

                            node_pin2 = doc.createElement('Pin')
                            node_pin2.setAttribute('PinDefinition', 'CAN_L')
                            node_pin2.setAttribute('PinNumber', '14')
                            node_protocol_k.appendChild(node_pin2)
                        node_name_protocol.appendChild(node_protocol_k)

                    header_manager.appendChild(node_name_protocol)

                else:
                    if '-' not in value[0]:
                        node_name = doc.createElement(value[0])
                        node_name.appendChild(doc.createTextNode(str(value[1])))
                        header_manager.appendChild(node_name)
        root.appendChild(header_manager)

        # did list
        did_list = {k: v for k, v in self.xml_did_list.items() if v}
        node_did_list = doc.createElement('DidList')
        if did_list:
            for key, val in did_list.items():
                node_did_item = doc.createElement('DidItem')
                for k in self.__did_order:
                    did_item_s = doc.createElement(k)
                    did_item_s.appendChild(doc.createTextNode(str(val[k])))
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

                # ParameterName
                parameter_name = val['parameter_name']
                byte = dict(val['byte'])

                for parameter_val in parameter_name:
                    node_parameter = doc.createElement('Parameter')

                    try:
                        default_val = val['conf_data'].get(list(parameter_val.keys())[0])[0][0]
                    except Exception:
                        default_val = ''

                    node_parameter.setAttribute('ParamDefaultValue', default_val)
                    for parameter_k, parameter_v in parameter_val.items():

                        # parameter and byte bit bit_len
                        byte_content = byte.get(parameter_k)

                        # bite
                        if byte_content:
                            byte_content = byte_content[0]
                            for p_key in self.__parameter_order():
                                node_byte_name = doc.createElement(p_key)
                                node_byte_name.appendChild(doc.createTextNode(str(byte_content.get(p_key))))
                                node_modification_item.appendChild(node_byte_name)

                        # ConfData
                        node_conf_data = doc.createElement('ConfData')
                        conf_data = val['conf_data'].get(parameter_k)

                        if not conf_data:
                            node_conf_data.setAttribute('useConfData', 'no')
                            node_parameter.appendChild(node_conf_data)

                        if conf_data:
                            node_conf_data.setAttribute('useConfData', 'true')
                            for data in conf_data:
                                node_config_data = doc.createElement('ConfigData')
                                node_config_data.setAttribute('Value', data[0])

                                node_config_data.setAttribute('ConfigExpression', data[1])
                                node_conf_data.appendChild(node_config_data)

                                node_parameter.appendChild(node_conf_data)

                    node_modification_item.appendChild(node_parameter)
                node_modification.appendChild(node_modification_item)
        root.appendChild(node_modification)

        node_write_section = doc.createElement('WriteSection')
        if self.read_section:
            for val in self.read_section:
                node_write_item = doc.createElement('WriteItem')
                node_write_item.setAttribute('DelayForMS', '0')
                node_write_item.setAttribute('DidWriteScope', 'All')
                node_write_item.setAttribute('IDREF', val)
                node_write_section.appendChild(node_write_item)
        root.appendChild(node_write_section)

        # RevisionLog
        node_log = doc.createElement('RevisionLog')
        node_log_entry = doc.createElement('RevisionLogEntry')

        log_file_number = doc.createElement('ConfigurationFileNumber')
        log_file_number.appendChild(doc.createTextNode(str(manager_dict.get('ConfigurationFileNumber'))))
        node_log_entry.appendChild(log_file_number)

        node_log_date = doc.createElement('RevisionDate')
        node_log_date.appendChild(doc.createTextNode(datetime.datetime.now().strftime('%Y-%m-%d')))
        node_log_entry.appendChild(node_log_date)

        node_log_description = doc.createElement('RevisionDescription')
        node_log_description.appendChild(doc.createTextNode('intinal version'))
        node_log_entry.appendChild(node_log_description)

        node_log_author = doc.createElement('RevisionAuthor')
        project_user = Project.query.get_or_404(self.project_id)
        node_log_author.appendChild(doc.createTextNode(project_user.user.username))
        node_log_entry.appendChild(node_log_author)

        node_log.appendChild(node_log_entry)
        root.appendChild(node_log)

        return doc

    def run(self):
        files_path = self.set_path()
        doc = self.set_xml()
        fp = open(files_path, 'w', encoding='utf-8')
        doc.writexml(fp, indent='\t', addindent='\t', newl='\n', encoding="utf-8")

    def mk_dir(self, project_name):
        files_path = self.set_dir_path(project_name)
        doc = self.set_xml()
        fp = open(files_path, 'w', encoding='utf-8')
        doc.writexml(fp, indent='\t', addindent='\t', newl='\n', encoding="utf-8")


if __name__ == '__main__':
    export_xml = ExportXml(1)
    export_xml.run()
