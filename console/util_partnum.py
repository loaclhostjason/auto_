import json
import sys
import os
from .config import Config
from .app.main.models import Project, ProjectRelation, ProjectPartNumber, ProjectPartNumRelation, ProjectPartNumberAttr
from .app.manage.models import AttrContent, Attr
from console.dom import minidom
from collections import OrderedDict, defaultdict
from .util_xml import UtilXml
from .util import ExportXml

os_name = sys.platform
operate = '\n' if os_name.startswith('win') else '\r\n'


class UtilPartNum(ExportXml):
    def __init__(self, *args, **kwargs):
        super(UtilPartNum, self).__init__(*args, **kwargs)
        # self.project_id = project_id

    @property
    def project_info(self):
        project = Project.query.filter_by(id=self.project_id).first()
        return project

    def set_part_path(self):
        project = self.project_info
        if not project:
            return
        real_path = Config.PART_PATH_ROOT
        files_path = os.path.join(real_path,
                                  '{}_{}.Part'.format(project.project_group.name, project.name))
        return files_path

    def get_part_list(self, part_num_relation_id):
        part_num = ProjectPartNumber.query. \
            filter_by(project_id=self.project_id, part_num_relation_id=part_num_relation_id). \
            order_by(ProjectPartNumber.id).all()

        if not part_num:
            return
        r = [{
            'number': v.number,
            'las': v.las} for v in part_num]
        return r

    @property
    def part_relation_info(self):
        part_relation = ProjectPartNumRelation.query.filter_by(project_id=self.project_id, level=2).order_by(
            ProjectPartNumRelation.relation_order).all()
        if not part_relation:
            return
        part_relation = [v.id for v in part_relation if v.id]
        return part_relation

    def part_attr_info(self, part_num_relation_id):
        part_attr = ProjectPartNumberAttr.query. \
            filter_by(project_id=self.project_id, part_num_relation_id=part_num_relation_id).first()
        if not part_attr:
            return '', ''
        return part_attr.name, part_attr.did

    def set_part_xml(self):
        doc = minidom.Document()
        root = doc.createElement('ConfigurationModule')

        root.setAttribute('%s-CONFIG-SCHEMA-VERSION' % self.xml_managers_attr, '1.0')
        doc.appendChild(root)

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
            protocols_order = OrderedDict()
            if new_protocols:
                for nk in order_protocols:
                    protocols_order[nk] = new_protocols.get(nk)

            node_name_protocol = doc.createElement('Protocol')
            inter_val = True
            for value in manager_list:
                if '-' in value[0] and inter_val:
                    inter_val = False
                    for nk, nv in protocols_order.items():
                        node_protocol_k = doc.createElement(nk)
                        if nv:
                            for nvv in nv:
                                node_protocol_k_name = doc.createElement(nvv[0])
                                node_protocol_k_name.appendChild(doc.createTextNode(str(nvv[1])))
                                node_protocol_k.appendChild(node_protocol_k_name)
                        if nk == 'PhysicalLayer':
                            pin_data = self.xml_pin
                            if pin_data:
                                pin_num = len(pin_data)
                                for pnum in range(pin_num):
                                    node_pin = doc.createElement('Pin')
                                    for cv in pin_data[pnum]:
                                        node_pin.setAttribute(cv['item'], cv['item_value'])
                                    node_protocol_k.appendChild(node_pin)
                        node_name_protocol.appendChild(node_protocol_k)

                    header_manager.appendChild(node_name_protocol)

                else:
                    if '-' not in value[0]:
                        node_name = doc.createElement(value[0])
                        node_name.appendChild(doc.createTextNode(str(value[1])))
                        header_manager.appendChild(node_name)
        root.appendChild(header_manager)

        part_list = doc.createElement('PartList')

        part_info = self.part_relation_info
        if part_info:
            for part_id in part_info:
                part_attr_name, part_attr_did = self.part_attr_info(part_id)
                part_num_doc = doc.createElement('PartNums')
                part_num_doc.setAttribute('Name', part_attr_name)
                part_num_doc.setAttribute('DID', part_attr_did)

                part_num_data = self.get_part_list(part_id)
                if part_num_data:
                    for pn in part_num_data:
                        part_num_info_doc = doc.createElement('PartNum')
                        part_num_info_doc.setAttribute('Value', pn['number'])
                        part_num_info_doc.setAttribute('Condition', UtilXml().change_data(pn['las']))
                        part_num_doc.appendChild(part_num_info_doc)
                part_list.appendChild(part_num_doc)

        root.appendChild(part_list)
        root.appendChild(self.xml_log(manager_dict, doc))
        return doc

    def run(self):
        files_path = self.set_part_path()
        if not files_path:
            return

        doc = self.set_part_xml()
        with open(files_path, 'w', encoding='utf-8') as f:
            doc.writexml(f, indent='', addindent='  ', newl=operate, encoding="utf-8")

        file_data = ""
        with open(files_path, 'r', encoding='UTF-8') as f:
            for line in f:
                file_data += line[:-1] + operate

        with open(files_path, 'w', encoding='utf-8') as f:
            f.write(file_data)
