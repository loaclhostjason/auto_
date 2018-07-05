from flask import request


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
