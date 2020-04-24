from .models import *


def str_to_hex(data, did_len=None):
    if not data:
        return
    init_de = '00'
    try:
        data_len = len(data) // 8 if not did_len else int(did_len)

        hex_data = hex(int(data, 2))
        hex_data = hex_data.replace('0x', '')
        hex_data = '0{}'.format(hex_data) if len(hex_data) % 2 else hex_data

        if (data_len - (len(hex_data) // 2)) >= 1:
            dif_len = data_len - (len(hex_data) // 2)
            hex_data = (init_de * dif_len) + hex_data
    except Exception as e:
        print('hex %s' % e)
        hex_data = data
    return hex_data


def _did_default_info(project_id):
    from collections import defaultdict
    project_data = ProjectData.query.filter_by(project_id=project_id).all()
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


def init_default_val(did_len, init_val):
    r = list()
    for index in range(did_len):
        r.append('00000000')

    if init_val:
        return init_val
    return r


def get_did_default_val(project_id):
    project_data = _did_default_info(project_id)
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

            init_val = init_default_val(did_len, init_val)

            # 跨字节 默认值
            if info.default_conf:
                if end_bit > 8:
                    #print("kuazijie")
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
    return r


def update_default_val(project_id, project_relation_id):
    all_default_conf = get_did_default_val(project_id)

    is_have = str(list(all_default_conf.values())[0]).replace('0', '')
    print(is_have)

    if is_have:
        pr = ProjectRelation.query.filter_by(id=project_relation_id).first()
        if pr:
            _attr_content = AttrContent.query.filter_by(project_relation_id=pr.id).first()
            cc = json.loads(_attr_content.real_content or '{}') if _attr_content else {}
            cc['DefaultValue'] = str_to_hex(all_default_conf[pr.id])
            _attr_content.real_content = json.dumps(cc)
            db.session.add(_attr_content)
            db.session.commit()
