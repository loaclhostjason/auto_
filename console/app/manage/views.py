from . import manage
from flask import render_template
from flask_login import login_required
from ..decorators import role_required
from .models import *


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
    return render_template('manage/edit_attrs.html', attr_info=attr_info)
