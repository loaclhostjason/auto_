from flask import request
from collections import defaultdict


def get_extra_content():
    field_key = [
        'item',
        'item_value',
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


def get_extra_section_content():
    field_key = [
        'resetsection_item',
        'resetsection_item_value',
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


def get_extra_content2(project_id=None):
    field_key = [
        'item',
        'item_value',
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
                if key == 'resetsection':
                    d['project_id'] = project_id
                result[key].append({k: v for k, v in d.items() if v})
    return {k: v for k, v in result.items() if v}
