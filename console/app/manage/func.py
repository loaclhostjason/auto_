from flask import request
from collections import defaultdict


def get_content():
    field_key = [
        'item',
        'item_protocol',
        'item_zh',
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
        'item_zh',
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
