from . import manage
from flask import render_template, flash, redirect, url_for
from flask_login import login_required
from ..decorators import role_required
from .models import *
from .func import *
import json


@manage.route('/attrs', methods=['GET', 'POST'])
@login_required
@role_required
def attrs():
    attr_list = Attr.query.all()
    return render_template('manage/attrs.html', attr_list=attr_list)


@manage.route('/attrs/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required
def edit_attr(id):
    attr_info = Attr.query.filter_by(id=id).first_or_404()

    if request.method == 'POST':
        content = get_content()
        data = {
            'content': json.dumps(content)
        }
        Attr.edit(data, attr_info)
        flash({'success': '更新成功'})
        return redirect(url_for('.attrs'))

    return render_template('manage/edit_attrs.html', attr_info=attr_info)
