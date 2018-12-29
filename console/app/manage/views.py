from . import manage
from flask import render_template, flash, redirect, url_for, current_app, jsonify
from flask_login import login_required
from ..decorators import role_required
from .models import *
from .func import *
import json
from .forms import *
from ..base import Check
import os
from ..main.models import ProjectGroup


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
    aciton = request.args.get('action')

    if request.method == 'POST':
        content = get_content()
        data = {
            'content': json.dumps(content)
        }
        Attr.edit(data, attr_info)
        if aciton == 'json':
            return jsonify({'success': True, 'message': '更新成功'})
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
    project_groups = ProjectGroup.query.all()

    las = Las.query.all()
    las = {v.project_group_id: v.file_name for v in las if v.file_name}
    return render_template('manage/las.html', project_groups=project_groups, las=las)


@manage.route('/las/create', methods=['GET', 'POST'])
@login_required
@role_required
def create_edit_las_file():
    form = LasFileForm()
    group_id = request.args.get('group_id')
    las = Las.query.filter_by(project_group_id=group_id).first()
    path = os.path.join(current_app.config['LAS_FILE_PATH_ROOT'])

    Check(form).check_validate_on_submit()
    if form.validate_on_submit():

        form_data = form.get_form_data()
        form_data['project_group_id'] = group_id

        file = request.files.get('file')
        if not file:
            form_data['file'] = las.file if las else None
            form_data['file_name'] = las.file_name if las else None
        else:
            form_data['file'], form_data['file_name'] = upload_file(path, file, las, group_id)

        if las:
            form.populate_obj(las)

        Las.edit_or_create_las(form_data, las, path)
        flash({'success': '更新成功！'})
        return redirect(url_for('.las'))

    if las:
        form.set_form_data(las)
    return render_template('manage/create_las_file.html', form=form)


@manage.route('/las/delete', methods=['POST'])
@login_required
@role_required
def delete_las_file():
    path = os.path.join(current_app.config['LAS_FILE_PATH_ROOT'])
    group_id = request.args.get('group_id')
    las = Las.query.filter_by(project_group_id=group_id).first()
    if not las:
        return jsonify({'success': False, 'message': '没有数据'})

    del_os_filename(path, las.file)
    las.file_name = None
    las.file = None
    db.session.add(las)
    return jsonify({'success': True, 'message': '更新成功'})


@manage.route('/project/group', methods=['GET', 'POST'])
@login_required
@role_required
def project_group():
    action = request.args.get('action')
    if request.method == 'POST':
        name = request.form.get('name')
        id = request.form.get('id')

        old_name = ProjectGroup.query.filter_by(name=name).first()
        if not name or not action:
            return jsonify({'success': False, 'message': '参数错误'})

        if action == 'edit':
            group_p = ProjectGroup.query.filter_by(id=id).first()
            if old_name and group_p.name != name:
                return jsonify({'success': False, 'message': '项目名称重复了'})
            group_p.name = name
            db.session.add(group_p)

        if action == 'create':
            if old_name:
                return jsonify({'success': False, 'message': '项目名称重复了'})
            project = ProjectGroup(name=name)
            db.session.add(project)

        return jsonify({'success': True, 'message': '更新成功'})

    project_groups = ProjectGroup.query.all()
    return render_template('manage/project_group.html', project_groups=project_groups)


@manage.route('/project/group/delete/<int:id>', methods=['POST'])
@login_required
@role_required
def delete_project_group(id):
    project_group_info = ProjectGroup.query.filter_by(id=id).first()
    if not project_group_info:
        return jsonify({'success': False, 'message': '参数错误'})

    # todo some bug
    las = project_group_info.las
    if len(las):
        return jsonify({'success': False, 'message': 'las 关联中'})
    users = project_group_info.users
    if len(users):
        return jsonify({'success': False, 'message': 'users 关联中'})
    projects = project_group_info.project
    if len(projects):
        return jsonify({'success': False, 'message': 'projects 关联中'})
    db.session.delete(project_group_info)
    return jsonify({'success': True, 'message': '更新成功'})


@manage.after_request
def after_request(response):
    from ..main.models import Project
    if not request.url_rule or request.method != 'POST':
        return response

    if request.url_rule.rule != '/manage/attr/content/add':
        return response

    project_id = request.args.get('project_id')

    project = Project.query.filter_by(id=project_id).first()
    if not project:
        return response

    project.last_time = datetime.now()

    db.session.add(project)
    db.session.commit()
    return response
