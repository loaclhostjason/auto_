from . import manage
from flask import render_template, flash, redirect, url_for, current_app
from flask_login import login_required
from ..decorators import role_required
from .models import *
from .func import *
import json
from .forms import *
from ..base import Check
import os


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


@manage.route('/attrs/extra/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required
def edit_extra_attr(id):
    attr_info = Attr.query.filter_by(id=id).first_or_404()
    level = attr_info.level
    extra_attr = ExtraAttrContent.query.filter_by(attr_id=id).first()
    if not extra_attr:
        extra_attr = ExtraAttrContent(attr_id=id)

    if request.method == 'POST':
        if level == 1:
            content = get_extra_content()
            content_section = get_extra_reset_content()
            pin_num = request.form.get('pin_num')
            content.append({'pin_num': pin_num})
            data = {
                'content': json.dumps([v for v in content if v]),
                'content_section': json.dumps([v for v in content_section if v])
            }
            ExtraAttrContent.edit(data, extra_attr)
        else:
            content = get_extra_content2()
            data = {
                'content': json.dumps(content)
            }
            ExtraAttrContent.edit(data, extra_attr)
            # return render_template('manage/edit_extra_attrs2.html', attr_info=attr_info, extra_attr=extra_attr)
        return redirect(url_for('.attrs'))

    if level == 1:
        return render_template('manage/edit_extra_attrs.html', attr_info=attr_info, extra_attr=extra_attr)
    else:
        return render_template('manage/edit_extra_attrs2.html', attr_info=attr_info, extra_attr=extra_attr)


@manage.route('/las')
@login_required
@role_required
def las():
    from ..main.models import Project
    project_names = Project.query.group_by(Project.project_name).all()

    las = Las.query.all()
    las = {v.project_name: v.file_name for v in las if v.file_name}
    return render_template('manage/las.html', project_names=project_names, las=las)


@manage.route('/las/create', methods=['GET', 'POST'])
@login_required
@role_required
def create_edit_las_file():
    form = LasFileForm()
    project_name = request.args.get('project_name')
    las = Las.query.filter_by(project_name=project_name).first()
    path = os.path.join(current_app.config['LAS_FILE_PATH_ROOT'])

    Check(form).check_validate_on_submit()
    if form.validate_on_submit():

        form_data = form.get_form_data()
        form_data['project_name'] = project_name

        file = request.files.get('file')
        if not file:
            form_data['file'] = las.file if las else None
            form_data['file_name'] = las.file_name if las else None
        else:
            form_data['file'], form_data['file_name'] = upload_file(path, file, las)

        if las:
            form.populate_obj(las)

        Las.edit_or_create_las(form_data, las, path)
        flash({'success': '更新成功！'})
        return redirect(url_for('.las'))

    if las:
        form.set_form_data(las)
    return render_template('manage/create_las_file.html', form=form)
