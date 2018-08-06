from flask import request
from collections import defaultdict
import os


def get_content():
    field_key = [
        'item',
        'item_protocol',
        'item_zh',
        'item_default',
        'item_required',
    ]
    items = request.form.getlist('item')
    if not items:
        return

    result = list()
    for index, val in enumerate(items):
        d = dict()
        for k in field_key:
            try:
                dict_value = request.form.getlist(k)[index]
                if dict_value:
                    d[k] = dict_value
            except Exception:
                pass
        result.append(d)
    return result


def get_extra_content():
    field_key = [
        'item',
        'item_default',
    ]
    items = request.form.getlist('item')
    if not items:
        return

    result = list()
    for index, val in enumerate(items):
        d = dict()
        for k in field_key:
            try:
                dict_value = request.form.getlist(k)[index]
                if dict_value:
                    d[k] = dict_value
            except Exception:
                pass
        result.append(d)
    return result


def get_extra_reset_content():
    field_key = [
        'resetsection_item',
        'resetsection_item_default',
    ]
    items = request.form.getlist('resetsection_item')
    if not items:
        return

    result = list()
    for index, val in enumerate(items):
        d = dict()
        for k in field_key:
            try:
                dict_value = request.form.getlist(k)[index]
                if dict_value:
                    d[k] = dict_value
            except Exception:
                pass
        result.append(d)
    return result


def get_extra_content2():
    field_key = [
        'item',
        'item_zh',
    ]
    field_keys = {
        'readsection': field_key,
        'writsection': field_key,
        'resetsection': field_key,
    }

    result = defaultdict(list)
    for key, val in field_keys.items():
        items = request.form.getlist('%s_%s' % (key, val[0]))
        if items:

            for index, val in enumerate(items):
                d = dict()
                for k in field_key:
                    try:
                        dict_value = request.form.getlist('%s_%s' % (key, k))[index]
                        if dict_value:
                            d[k] = dict_value
                    except Exception:
                        pass
                result[key].append(d)
    return {k: v for k, v in result.items() if v}


'''
00000000000000000

'''


def del_os_filename(base_path, filename):
    for root, dirs, files in os.walk(base_path, topdown=False):
        for name in files:
            if filename and filename == name:
                os.remove(os.path.join(root, name))


def upload_file(path, file, data, project_group_id):
    if data:
        del_os_filename(path, data.file)

    save_filename = '[%s]%s' % (project_group_id, file.filename)
    file.save(os.path.join(path, save_filename))
    return save_filename, file.filename
