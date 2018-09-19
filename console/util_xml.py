# coding:utf-8
from .app.main.models import Project, ProjectRelation, ProjectData
from .app.manage.models import AttrContent, Attr
import re
from collections import defaultdict, OrderedDict
import json

sty = {
    '#': '+',
    '&': '.',
    '/': '+',
    '-': '-',
}


class XmlData(object):
    def __init__(self, project_id):
        self.project_id = project_id

    @staticmethod
    def init_default_val(did_len, init_val):
        r = list()
        for index in range(did_len):
            r.append('00000000')

        if init_val:
            return init_val
        return r

    @property
    def _did_default_info(self):
        project_data = ProjectData.query.filter_by(project_id=self.project_id).all()
        r = defaultdict(list)
        if not project_data:
            return r
        for info in project_data:
            project_relation = ProjectRelation.query.filter_by(id=info.project_relation_id).first()
            project_relation = ProjectRelation.query.filter_by(
                id=project_relation.parent_id if project_relation else '').first()
            if project_relation:
                r[project_relation.parent_id].append(info)
        return r

    def get_did_default_val(self):
        from .app.main.api_data import split_default_val
        project_data = self._did_default_info
        if not project_data:
            return

        r = dict()
        for parent_id, datas in project_data.items():
            init_val = []
            for info in datas:
                did_len = AttrContent.get_did_len(parent_id)
                bit_len, start_bit, byte_info, ext_bit = AttrContent.get_attr_info(info.project_relation_id,
                                                                                   show_ext_bit=True)

                end_bit = start_bit + bit_len

                init_val = self.init_default_val(did_len, init_val)

                # 跨字节 默认值
                if info.default_conf:
                    info.default_conf = split_default_val(info.default_conf, bit_len)
                    if end_bit > 8:
                        b_len = end_bit - 8

                        d1 = info.default_conf[:-b_len]
                        d2 = info.default_conf[-b_len:]

                        __init_val_01 = init_val[byte_info][::-1]
                        __init_val_02 = init_val[int(byte_info) + 1][::-1]

                        __init_val_01 = __init_val_01[0:start_bit] + d1[::-1]
                        __init_val_02 = __init_val_02[0:ext_bit] + d2[::-1] + __init_val_02[b_len + ext_bit:]

                        init_val[byte_info] = __init_val_01[::-1]
                        init_val[int(byte_info) + 1] = __init_val_02[::-1]

                    else:
                        __init_val = init_val[byte_info][::-1]
                        __init_val = __init_val[0:start_bit] + info.default_conf[::-1] + __init_val[end_bit:]

                        # print(__init_val)
                        init_val[byte_info] = __init_val[::-1]

                r[parent_id] = init_val

        r = {k: ''.join([v for v in list_val]) for k, list_val in r.items()}
        # print(r)
        return r

    @staticmethod
    def _get_xml_extra_pin_data(content):
        if not content:
            return list()
        pin_num = content[-1].get('pin_num')
        pin_num = int(pin_num)
        content = [
            {
                'item': v['item'],
                'item_value': v['item_default']
            } for v in content[:-1] if v.get('item_default')
        ]
        content = content * pin_num
        result = [content[i:i + len(content) // 2] for i in range(0, len(content), len(content) // 2)]
        return result

    @staticmethod
    def _get_xml_pin_data(content):
        result = {
            'pin_num': 0,
            'data': list()
        }
        for c in content:
            if 'pin_num' in c.keys():
                result['pin_num'] = int(c['pin_num'])
            else:
                result['data'].append(c)

        data = result['data']
        if data:
            result = [data[i:i + len(data) // 2] for i in range(0, len(data), len(data) // 2)]
        return result

    @staticmethod
    def get_ext_conf_data(bit_info, default_val):
        d = {
            'ParamDefaultValue': default_val,
            'ParameterName': bit_info['parameter_name'],
            'BytePosition': bit_info['byte_info'] + 2,
            'BitPosition': bit_info['ext_bit'],
            'BitLength': bit_info['start_bit'] + bit_info['bit_len'] - 8,
        }
        return d


# todo no use
class UtilXml(object):
    def __init__(self):
        pass

    @staticmethod
    def get_parent_id(info):
        project_relation = ProjectRelation.query.filter_by(id=info.project_relation_id).first()
        project_relation = ProjectRelation.query.filter_by(
            id=project_relation.parent_id if project_relation else '').first()
        if not project_relation:
            return
        return project_relation.parent_id

    @staticmethod
    def check_las(new_data_init):
        if '$' in new_data_init:
            return new_data_init

        result = []
        split_re = '|\\'.join(sty.keys())
        split_re = '(\\' + split_re + ')'
        split_data = re.split(r'%s' % split_re, new_data_init)

        if split_data:
            for dl in split_data:
                if dl not in sty.keys():
                    result.append('$' + dl)
                else:
                    result.append(dl)
        else:
            result = '$' + new_data_init

        if isinstance(result, list):
            result = ''.join(result)
        return result

    def change_data(self, new_data_init):
        if str(new_data_init).lower() in ['none', 'all']:
            return ''
        if not new_data_init:
            return ''

        hav_i = False
        if "!" in new_data_init:
            new_data_init = new_data_init[2:-1]
            hav_i = True

        new_data_init = self.check_las(new_data_init)

        new_data = ''
        if '/' in new_data_init:
            data = new_data_init.split('/')
            for index, v in enumerate(data):
                if index == 0:
                    try:
                        tmp_s = v[-6]
                        tmp = v.split(tmp_s)
                        tmp = [v for v in tmp if v]
                        new_data += ''.join(tmp[:-1]) + tmp_s + '(' + ''.join(tmp[-1])
                    except Exception as e:
                        new_data += '(' + v
                else:
                    if index < len(data) - 1:
                        if len(v) > 5:
                            new_data += '/' + v[:5] + ')' + v[5:-5] + '(' + v[-5:]
                        else:
                            new_data += '/' + v
                    else:
                        new_data += '/' + v + ')'
        else:
            new_data = new_data_init

        if '#' in new_data:
            n = new_data.split('#')
            new_data = ['(%s)' % v for v in n if v]
            new_data = '+'.join(new_data)

        for k, v in sty.items():
            new_data = new_data.replace(k, v)

        if hav_i:
            new_data = '!(' + new_data + ')'
        return new_data

    @staticmethod
    def change_las_data(new_data_init):
        if str(new_data_init).lower() in ['none', 'all']:
            return ''
        if not new_data_init:
            return ''
        data = re.split(r'(\w{4})+', str(new_data_init).strip())

        data = [v for v in data if v]
        r = list()
        if data:
            for info in data:
                if re.findall(r"(\w{4})+", info):
                    info = '$' + info
                info = info.replace('&', '.')
                r.append(info)
        r = ''.join(r)
        return r

    @staticmethod
    def get_ecu_order():
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

    @staticmethod
    def get_did_order():
        attr = Attr.query.filter_by(level=2).first()
        if not attr or not attr.content:
            return []
        content = json.loads(attr.content)
        result = list()
        for v in content:
            result.append(v['item'])
        return result

    @staticmethod
    def get_parameter_order():
        attr = Attr.query.filter_by(level=3).first()
        if not attr or not attr.content:
            return list()
        result = list()
        content = json.loads(attr.content)
        for ar in content:
            if ar.get('item') and ar.get('item') != 'ExtBitPosition':
                result.append(ar['item'])
        return result
