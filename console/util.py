# import xml.dom.minidom
from console.dom import minidom
import os
import json
from .app.main.models import Project, ProjectRelation, ProjectData
from .app.manage.models import AttrContent, Attr, ExtraAttrData
from .app.models import Modification
from collections import defaultdict, OrderedDict
import datetime
import re
import sys
from .util_xml import XmlData, UtilXml

os_name = sys.platform
operate = '\n' if os_name.startswith('win') else '\r\n'

sty = {
    '#': '+',
    '&': '.',
    '/': '+',
    '-': '-',
}


class ExportXml(XmlData):

    def __init__(self, *args, **kwargs):
        super(ExportXml, self).__init__(*args, **kwargs)
        # self.project_id = project_id

    def set_path(self):
        if not self.xml_managers_attr:
            return
        path = os.path.abspath(os.path.dirname(__file__))
        real_path = os.path.join(path, 'files', 'all')
        files_path = os.path.join(real_path, '%s.95' % self.xml_managers_attr)

        if not os.path.exists(real_path):
            os.makedirs(real_path)
        return files_path

    def set_dir_path(self, project_name):
        if not self.xml_managers_attr:
            return
        path = os.path.abspath(os.path.dirname(__file__))
        real_path = os.path.join(path, 'files', project_name)
        files_path = os.path.join(real_path, '%s.95' % self.xml_managers_attr)

        if not os.path.exists(real_path):
            os.makedirs(real_path)
        return files_path

    @property
    def xml_managers_attr(self):
        project = Project.query.get_or_404(self.project_id)
        # result = '{}_{}'.format(project.project_group.name, project.name)
        result = project.project_config_name.lower()
        return result

    @property
    def xml_pin(self):
        attr = Attr.query.filter_by(level=1).first()
        extra_data = ExtraAttrData.query.filter_by(project_id=self.project_id, level=1).first()
        if not attr or not attr.extra_attr_content:
            return list()

        content = json.loads(extra_data.pin) if extra_data and extra_data.pin else []
        if not content:
            content = json.loads(attr.extra_attr_content.content or '{}') if attr.extra_attr_content else []
            return self._get_xml_extra_pin_data(content)

        return self._get_xml_pin_data(content)

    @property
    def xml_header_attr(self):
        result = OrderedDict()
        project_relation = ProjectRelation.query.filter_by(project_id=self.project_id, parent_id=None).first()

        if not project_relation:
            return list(), dict()

        attr_content = AttrContent.query.filter_by(project_relation_id=project_relation.id).first()

        header, *arg = self.default_attr
        header_default = [
            (((v['item_protocol'] + '-') if v.get('item_protocol') else '') + v['item'], v['item_default'])
            for v in header if v.get('item') and v.get('item_default')]

        if not attr_content or not attr_content.real_content:
            if not header:
                return list(), dict()
            else:
                return header_default, dict(header_default)

        content = json.loads(attr_content.real_content)

        order_content = UtilXml.get_ecu_order()
        if order_content:
            for oc in order_content:
                result[oc] = content.get(oc) or dict(header_default).get(oc, '')

        result_list = [(key, val) for key, val in result.items()]
        return result_list, dict(result)

    @property
    def xml_did_list(self):
        # default
        default_val_did = self.get_did_default_val()

        header, did, *args = self.default_attr
        did_default = {v['item']: v['item_default'] for v in did if v.get('item') and v.get('item_default')}

        result = OrderedDict()
        project_relation = ProjectRelation.query.filter_by(project_id=self.project_id, level=2). \
            order_by(ProjectRelation.relation_order).all()
        if not project_relation:
            return result

        for pr in project_relation:
            attr_content = AttrContent.query.filter_by(project_relation_id=pr.id).first()
            real_content = json.loads(attr_content.real_content) if attr_content and attr_content.real_content else {}
            if real_content:
                for k, v in real_content.items():
                    if not real_content.get(k):
                        real_content[k] = did_default.get(k, '')
            else:
                real_content = did_default

            if default_val_did and default_val_did.get(pr.id):
                real_content['DefaultValue'] = self.str_to_hex(default_val_did[pr.id])
            else:
                did_len = real_content.get('DidLength')
                real_content['DefaultValue'] = self.str_to_hex(real_content.get('DefaultValue'), did_len)
            result[pr.name] = real_content

        return result

    @property
    def read_section(self):
        project_relation = ProjectRelation.query.filter_by(project_id=self.project_id, level=2). \
            order_by(ProjectRelation.relation_order).all()
        result = [v.name for v in project_relation]
        return result

    def __get_(self, projects):
        *args, t_did = self.default_attr
        t_did = {v['item']: v['item_default'] for v in t_did if v.get('item') and v.get('item_default')}

        d = defaultdict(list)
        project_relation_ids = [project['project_relation_id'] for project in projects if
                                project.get('project_relation_id')]

        attr_content = AttrContent.query.filter(AttrContent.project_relation_id.in_(project_relation_ids)).all()
        pro = ProjectRelation.query.filter(ProjectRelation.id.in_(project_relation_ids)). \
            order_by(ProjectRelation.relation_order).all()

        d['parameter_name'] = [{p.id: p.name} for p in pro]
        r = defaultdict(list)
        if attr_content:
            for ac in attr_content:
                content = json.loads(ac.real_content) if ac and ac.real_content else None
                if content:
                    for k, v in content.items():
                        if not content.get(k):
                            content[k] = t_did.get(k, '')

                    byte_p = content.get('BytePosition')
                    bit_p = content.get('BitPosition')
                    bit_l = content['BitLength']

                    if byte_p:
                        content['BytePosition'] = int(byte_p) + 1

                    if bit_p and bit_l:
                        if int(bit_p) + int(bit_l) - 8 > 0:
                            content['BitPosition'] = 7
                        else:
                            content['BitPosition'] = int(bit_p) + (int(bit_l) - 1) if int(bit_l) > 0 else 0
                    if bit_l and bit_p and int(bit_l) + int(bit_p) > 8:
                        content['BitLength'] = 8 - int(bit_p)
                    r[ac.project_relation_id].append(content)

        this_id = [v.project_relation_id for v in attr_content]
        dif_id = list(set(project_relation_ids) - set(this_id))
        if len(dif_id):
            for id_info in dif_id:
                r[id_info].append(t_did)

        d['byte'] = r
        return d

    @staticmethod
    def str_to_hex(data, did_len=None):
        if not data:
            return
        init_de = '00'
        try:
            data_len = len(data) // 8 if not did_len else did_len

            hex_data = hex(int(data, 2))
            hex_data = hex_data.replace('0x', '')
            hex_data = '0{}'.format(hex_data) if len(hex_data) % 2 else hex_data

            if (data_len - (len(hex_data) // 2)) >= 1:
                dif_len = data_len - (len(hex_data) // 2)
                hex_data = (init_de * dif_len) + hex_data
        except Exception as e:
            print(e)
            hex_data = data
        return hex_data

    @property
    def modification(self):
        did = self.read_section
        r = defaultdict(list)
        if did:
            for v in did:
                project_relation = ProjectRelation.query.filter_by(name=v, project_id=self.project_id).first()
                if project_relation:
                    project_relation_child = ProjectRelation.query.filter_by(parent_id=project_relation.id).all()
                    if project_relation_child:
                        for pc in project_relation_child:
                            r[v].append({'project_relation_id': pc.id})

        new_result = dict()

        if r:
            for address, projects in r.items():
                modification = Modification.query.filter_by(project_id=self.project_id).first()
                modification = json.loads((modification.content or '{}')) if modification else None
                conf_data = modification.get('conf_data') if modification else {}
                ext_conf_data = modification.get('ext_conf_data') if modification else {}

                conf_data = {int(k): v for k, v in conf_data.items() if k}
                ext_conf_data = {int(k): v for k, v in ext_conf_data.items() if k}
                conf_data = {
                    'conf_data': conf_data,
                    'ext_conf_data': ext_conf_data,
                }
                new_result[address] = dict(conf_data, **self.__get_(projects))

        return new_result

    @property
    def __default_conf(self):
        mod_data = Modification.query.filter_by(project_id=self.project_id).first()

        default_ = dict()
        if mod_data:
            default_ = json.loads(mod_data.default_conf or '{}')

        if default_:
            default_ = {int(k): v for k, v in default_.items() if k}
        return default_

    @staticmethod
    def get_default_rw_sec(de_content, rw_type):
        # rw_type in readsection writsection
        result = [{
            'item': v['item'],
            'item_value': v['item_default']
        } for v in de_content[rw_type] if v.get('item_default')]
        result = [v for v in result if v]
        return result

    def xml_section_attr(self, did_name, type_result):
        extra_data = ExtraAttrData.query.filter_by(project_id=self.project_id, level=2).all()
        attr = Attr.query.filter_by(level=2).first()
        if not attr:
            return list()

        de_content = json.loads(
            attr.extra_attr_content.content) if attr.extra_attr_content and attr.extra_attr_content.content else {}

        read_section = None
        write_section = None

        if not extra_data:
            read_section = self.get_default_rw_sec(de_content, 'readsection')
            write_section = self.get_default_rw_sec(de_content, 'writsection')
        else:
            for ed in extra_data:
                read_sec = ed.read_sec
                write_sec = ed.write_sec
                if read_sec and ed.project_relation.name == did_name:
                    read_section = json.loads(read_sec)
                else:
                    read_section = self.get_default_rw_sec(de_content, 'readsection')

                if write_sec and ed.project_relation.name == did_name:
                    write_section = json.loads(write_sec)
                else:
                    write_section = self.get_default_rw_sec(de_content, 'writsection')

        result = {
            'read_section': read_section,
            'write_section': write_section,
        }
        return result.get(type_result)

    @property
    def xml_reset_section(self):
        attr = Attr.query.filter_by(level=1).first()
        extra_data = ExtraAttrData.query.filter_by(project_id=self.project_id, level=1).first()
        if not attr or not attr.extra_attr_content:
            return list(), list()

        content = json.loads(extra_data.reset_sec) if extra_data and extra_data.reset_sec else []
        if not content:
            content_sec = json.loads(
                attr.extra_attr_content.content_section or '{}') if attr.extra_attr_content else []
            content = [
                {
                    'resetsection_item': v['resetsection_item'],
                    'resetsection_item_value': v['resetsection_item_default']
                } for v in content_sec if v.get('resetsection_item_default')]

        extra_data_2 = ExtraAttrData.query.filter_by(project_id=self.project_id, level=2).all()
        new_reset_section = []
        if extra_data_2:
            for info in extra_data_2:
                if info.is_open_reset:
                    new_reset_section.append(info.project_relation.name)

        return content, new_reset_section

    @property
    def default_attr(self):
        attr_query = Attr.query

        header = attr_query.filter_by(level=1).first()
        did = attr_query.filter_by(level=2).first()
        t_did = attr_query.filter_by(level=3).first()

        header = json.loads(header.content) if header else []
        did = json.loads(did.content) if did else []
        t_did = json.loads(t_did.content) if t_did else []

        return header, did, t_did

    def set_xml(self):
        doc = minidom.Document()
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

        # did list
        node_did_list = doc.createElement('DidList')
        if self.xml_did_list:
            for key, val in self.xml_did_list.items():
                node_did_item = doc.createElement('DidItem')
                if val:
                    for k in UtilXml.get_did_order():
                        did_item_s = doc.createElement(k)
                        if k == 'FeatureCode':
                            did_item_s.appendChild(doc.createTextNode(UtilXml.change_las_data(str(val.get(k) or ''))))
                        else:
                            did_item_s.appendChild(doc.createTextNode(str(val.get(k) or '')))
                        node_did_item.appendChild(did_item_s)
                    node_did_list.appendChild(node_did_item)
        root.appendChild(node_did_list)

        # ReadSection
        section_manager = doc.createElement('ReadSection')
        if self.read_section:
            for v in self.read_section:
                node_name = doc.createElement('ReadItem')
                node_name.setAttribute('IDREF', v)

                read_section_attr = self.xml_section_attr(v, 'read_section')
                if read_section_attr:
                    for rs in read_section_attr:
                        node_name.setAttribute(rs['item'], rs['item_value'])
                section_manager.appendChild(node_name)
        root.appendChild(section_manager)

        # ModificationSection
        modification_section = self.modification
        node_modification = doc.createElement('ModificationSection')
        if modification_section:
            for key in self.read_section:
                val = modification_section.get(key)
                if val:
                    node_modification_item = doc.createElement('ModificationItem')
                    node_modification_item.setAttribute('IDREF', key)

                    # ParameterName
                    parameter_name = val['parameter_name']
                    byte = dict(val['byte'])

                    for parameter_val in parameter_name:
                        node_parameter = doc.createElement('Parameter')

                        default_conf = self.__default_conf
                        if not parameter_val:
                            parameter_val = {}

                        parameter_val_kk = list(parameter_val.keys())[0] if parameter_val else 0
                        if default_conf.get(parameter_val_kk):
                            default_val = default_conf[parameter_val_kk]
                        else:
                            default_val = ''

                        try:
                            _config_data_las = dict(val['conf_data'].get(parameter_val_kk))
                        except Exception as e:
                            _config_data_las = {}

                        _config_data_las = [v.lower() for v in _config_data_las.values() if v]
                        if 'all' not in _config_data_las:
                            node_parameter.setAttribute('ParamDefaultValue',
                                                        self.str_to_hex(str(default_val or '')))
                            for parameter_k, parameter_v in parameter_val.items():

                                # parameter and byte bit bit_len
                                byte_content = byte.get(parameter_k)

                                # bite
                                if byte_content:
                                    byte_content = byte_content[0]
                                    for p_key in UtilXml.get_parameter_order():
                                        node_byte_name = doc.createElement(p_key)
                                        node_byte_name.appendChild(
                                            doc.createTextNode(str(byte_content.get(p_key, ''))))
                                        node_parameter.appendChild(node_byte_name)

                                # ConfData
                                node_conf_data = doc.createElement('ConfData')
                                conf_data = val['conf_data'].get(parameter_k)
                                conf_data = [(v[0], v[1]) for v in conf_data if
                                             v[0] and v[1]] if conf_data else None

                                if not conf_data:
                                    node_conf_data.setAttribute('useConfData', 'no')
                                    node_parameter.appendChild(node_conf_data)

                                if conf_data:
                                    node_conf_data.setAttribute('useConfData', 'true')
                                    for data in conf_data:
                                        node_config_data = doc.createElement('ConfigData')
                                        # if data[0] and data[1] and change_data(data[1]):
                                        if data[0] and data[1] and UtilXml.change_las_data(data[1]):
                                            node_config_data.setAttribute('Value', data[0])
                                            node_config_data.setAttribute('ConfigExpression',
                                                                          UtilXml.change_las_data(data[1]))
                                            node_conf_data.appendChild(node_config_data)

                                            node_parameter.appendChild(node_conf_data)
                                        if data[1] == 'all':
                                            node_parameter.appendChild(node_conf_data)
                                            break

                        # if _config_data_las:
                        if 'all' not in _config_data_las:
                            node_modification_item.appendChild(node_parameter)

                        _ext_conf_datas = val['ext_conf_data'].get(parameter_val_kk)
                        if _ext_conf_datas:
                            for _ext_conf_data in _ext_conf_datas:
                                ext_parameter = doc.createElement('Parameter')
                                ext_info = _ext_conf_data.get('info') or {}
                                ext_data = _ext_conf_data['data']
                                if ext_info:
                                    ext_parameter.setAttribute('ParamDefaultValue',
                                                               self.str_to_hex(
                                                                   str(ext_info.get('ParamDefaultValue', ''))))

                                    ext_parameter_name = doc.createElement('ParameterName')
                                    ext_parameter_name.appendChild(
                                        doc.createTextNode(str(ext_info.get('ParameterName', ''))))
                                    ext_parameter.appendChild(ext_parameter_name)

                                    ext_byte_name = doc.createElement('BytePosition')
                                    ext_byte_name.appendChild(doc.createTextNode(str(ext_info.get('BytePosition', ''))))
                                    ext_parameter.appendChild(ext_byte_name)

                                    ext_bit = doc.createElement('BitPosition')
                                    ext_bit.appendChild(doc.createTextNode(str(ext_info.get('BitPosition', ''))))
                                    ext_parameter.appendChild(ext_bit)

                                    ext_bit_len = doc.createElement('BitLength')
                                    ext_bit_len.appendChild(doc.createTextNode(str(ext_info.get('BitLength', ''))))
                                    ext_parameter.appendChild(ext_bit_len)

                                    ext_conf_d = doc.createElement('ConfData')
                                    ext_conf_d.setAttribute('useConfData', 'true')

                                    # print(ext_data)
                                    for v in ext_data:
                                        ext_config_data = doc.createElement('ConfigData')
                                        ext_config_data.setAttribute('Value', v[0])
                                        ext_config_data.setAttribute('ConfigExpression', UtilXml.change_las_data(v[1]))
                                        ext_conf_d.appendChild(ext_config_data)

                                    ext_parameter.appendChild(ext_conf_d)

                                node_modification_item.appendChild(ext_parameter)

                    node_modification.appendChild(node_modification_item)
        root.appendChild(node_modification)

        node_write_section = doc.createElement('WriteSection')
        if self.read_section:
            for val in self.read_section:
                node_write_item = doc.createElement('WriteItem')
                node_write_item.setAttribute('IDREF', val)
                read_section_attr = self.xml_section_attr(val, 'write_section')
                if read_section_attr:
                    for rs in read_section_attr:
                        node_write_item.setAttribute(rs['item'], rs['item_value'])
                node_write_section.appendChild(node_write_item)
        root.appendChild(node_write_section)

        # ResetSection
        node_reset_section = doc.createElement('ResetSection')
        reset_section_attr, read_section_val = self.xml_reset_section
        if reset_section_attr:
            for v in reset_section_attr:
                node_reset_section.setAttribute(v['resetsection_item'], v['resetsection_item_value'])
        if read_section_val:
            for info in read_section_val:
                node_reset_section_v = doc.createElement('ReadItem')
                node_reset_section_v.setAttribute('IDREF', info)
                node_reset_section.appendChild(node_reset_section_v)

        root.appendChild(node_reset_section)

        # RevisionLog
        root.appendChild(self.xml_log(manager_dict, doc))

        return doc

    def xml_log(self, manager_dict, doc):
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
        return node_log

    def run(self):
        files_path = self.set_path()
        if not files_path:
            return 'ConfigurationFileNumber no fund'

        doc = self.set_xml()
        with open(files_path, 'w', encoding='utf-8') as f:
            doc.writexml(f, indent='', addindent='  ', newl=operate, encoding="utf-8")

        file_data = ""
        with open(files_path, 'r', encoding='UTF-8') as f:
            for line in f:
                if '<DefaultValue' in line:
                    line = line[:20] + (('"' + line[20:-16] + '"') if line[20:-16] else '') + line[-16:-1] + operate
                else:
                    line = line[:-1] + operate
                file_data += line

        with open(files_path, 'w', encoding='utf-8') as f:
            f.write(file_data)

    def mk_dir(self, project_name):
        files_path = self.set_dir_path(project_name)
        if not files_path:
            return 'ConfigurationFileNumber no fund'

        doc = self.set_xml()
        with open(files_path, 'w', encoding='utf-8') as f:
            doc.writexml(f, indent='', addindent='  ', newl=operate, encoding="utf-8")

        file_data = ""
        with open(files_path, 'r', encoding='UTF-8') as f:
            for line in f:
                if '<DefaultValue' in line:
                    line = line[:20] + (('"' + line[20:-16] + '"') if line[20:-16] else '') + line[-16:-1] + operate
                else:
                    line = line[:-1] + operate
                file_data += line

        with open(files_path, 'w', encoding='utf-8') as f:
            f.write(file_data)
