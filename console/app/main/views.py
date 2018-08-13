# coding: utf-8
from flask import render_template, redirect, url_for, jsonify, abort, request, flash, current_app
from flask_login import login_required, current_user

from . import main
from .forms import *
from ..base import Check
from ..app import upload_files
from config import Config
import os
from datetime import datetime
from .models import *
from collections import defaultdict
from .func import *
from ..models import User
from sqlalchemy import or_, func

import json
from util import ExportXml
from ..manage.models import Attr, ExtraAttrContent
from .func_extra import *


@main.route('/sorry')
def sorry():
    return render_template('no.html')


@main.route('/', methods=['GET', 'POST'])
@main.route('/projects', methods=['GET', 'POST'])
@login_required
def projects():
    user = User.query.get_or_404(current_user.id)
    project_group_id = user.project_group_id

    project_query = Project.query.order_by(Project.project_group_id, Project.id)
    if current_user.is_admin:
        project_list = project_query.all()
    elif current_user.is_pm_admin:
        project_list = project_query.filter_by(project_group_id=project_group_id).all()
    else:
        project_list = project_query.filter_by(user_id=current_user.id).all()

    group_project = db.session.query(Project.id, Project.project_group_id,
                                     func.count(Project.id).label('project_num')).group_by(
        Project.project_group_id).all()

    group_project = {project_id: num for project_id, project_group_id, num in group_project}
    print(group_project)
    return render_template('main/projects.html', projects=project_list, group_project=group_project)


@main.route('/project/create_edit', methods=['GET', 'POST'])
@login_required
def create_edit_project():
    return render_template('main/create_edit_project.html')


@main.route('/project/edit/<int:project_id>', methods=['GET', 'POST'])
@login_required
def edit_file(project_id):
    project = Project.query.get_or_404(project_id)
    return render_template('main/create_edit_project.html', project=project)


@main.route('/project/edit/<int:project_id>/extra', methods=['GET', 'POST'])
@login_required
def edit_extra_attr_file(project_id):
    project = Project.query.get_or_404(project_id)
    level = request.args.get('level') or 0
    attr = Attr.query.filter_by(level=level).first()
    extra_attr = attr.extra_attr_content
    if not attr or not extra_attr:
        abort(404)

    if request.method == 'POST':
        content_val = json.loads(extra_attr.content_val) if extra_attr.content_val else {}
        content_section_val = json.loads(extra_attr.content_section_val) if extra_attr.content_section_val else {}

        pin_num = request.form.get('pin_num')
        if pin_num:
            content = get_extra_content()
            content.append({'pin_num': pin_num})
            content = {project_id: [v for v in content if v]}

            content_section = get_extra_section_content()
            content_section = {project_id: [v for v in content_section if v]}
            if not content_val.get(str(project_id)):
                content_val = dict(content, **content_val)
                content_section_val = dict(content_section, **content_section_val)
            else:
                content_val[str(project_id)] = content[project_id]
                content_section_val[str(project_id)] = content_section[project_id]

            extra_attr.content_val = json.dumps(content_val)
            extra_attr.content_section_val = json.dumps(content_section_val)

        else:
            name = request.args.get('name')
            reset_section = request.form.get('reset_section')

            c_all = content_val.values()
            resetsection = [v['resetsection'] for v in c_all if v['resetsection']]

            content = get_extra_content2(project_id)

            reset_section_d = defaultdict(list)
            if resetsection:
                for v in resetsection:
                    for kk, vv in v.items():
                        reset_section_d[kk].append(vv)

            reset_section_d = {k: list(set(sum(v, []))) for k, v in reset_section_d.items()}
            content['resetsection'] = {project_id: reset_section_d.get(project_id) or []}

            r = reset_section_d.get(project_id) or []
            if reset_section and name not in r:
                r.append(name)
                content['resetsection'][project_id].append(name)
            else:
                if content['resetsection'].get(project_id):
                    content['resetsection'][project_id].remove(name)

            if not name:
                abort(404)
            if not content_val.get(name):
                content_val = dict({name: content}, **content_val)
            else:
                content_val[name] = content
            extra_attr.content_val = json.dumps(content_val)
        db.session.add(extra_attr)
        return redirect(url_for('.edit_file', project_id=project_id))

    # todo ruan
    default_sec = {}
    default_write_attr = {}
    default_read_attr = {}
    if int(level) == 1:
        default_attr = json.loads(extra_attr.content) if extra_attr.content else {}
        default_sec = json.loads(extra_attr.content_section) if extra_attr.content_section else {}
        default_attr = {val['item']: val['item_default'] for val in default_attr if
                        val.get('item') and val.get('item_default')}
        default_sec = {val['resetsection_item']: val['resetsection_item_default'] for val in default_sec if
                       val.get('resetsection_item') and val.get('resetsection_item_default')}
    else:
        default_attr = json.loads(extra_attr.content) if extra_attr.content else {}
        if default_attr:
            default_read_attr = default_attr.get('readsection')
            default_read_attr = {val['item']: val['item_default'] for val in default_read_attr if
                                 val.get('item_default')}

            default_write_attr = default_attr.get('writsection')
            default_write_attr = {val['item']: val['item_default'] for val in default_write_attr if
                                  val.get('item_default')}

    if int(level) == 1:
        return render_template('main/create_edit_extra_attr_file.html', project=project, extra_attr=extra_attr,
                               default_attr=default_attr, default_sec=default_sec)
    else:
        return render_template('main/create_edit_extra_attr_file2.html', project=project, extra_attr=extra_attr,
                               default_read_attr=default_read_attr, default_write_attr=default_write_attr)


@main.after_request
def after_request(response):
    if not request.url_rule or request.method != 'POST':
        return response

    project_relation = ProjectRelation.query.order_by(ProjectRelation.timestamp.desc()).all()
    r = defaultdict(list)
    if project_relation:
        for pr in project_relation:
            r[pr.project_id].append(pr.timestamp)

    d = {k: max(v) for k, v in r.items() if v}
    if not d:
        return response

    for project_id, timestamp in d.items():
        project = Project.query.filter_by(id=project_id).first()
        if project and project.last_time < timestamp:
            project.last_time = timestamp
            db.session.add(project)
            db.session.commit()

    return response


@main.route('/download_file')
@login_required
def download_file():
    project_id = request.args.get('project_id')
    project = Project.query.get_or_404(project_id)
    export_xml = ExportXml(project_id)
    export_xml.mk_dir(project.project_group.name)
    export_xml.run()
    return download_files(project.project_config_name)


@main.after_request
def after_request(response):
    if request.url_rule.rule == '/download_file':
        response.headers['Set-Cookie'] = 'fileDownload=true; path=/'

    return response


@main.route('/project/edit/name', methods=['POST'])
@login_required
def edit_project_name():
    from .api import delete_project_file
    name = request.form.get('name')
    id = request.form.get('id')
    if not name:
        return jsonify({'success': False, 'message': '名称不能为空'})

    project_relation = ProjectRelation.query.filter_by(id=id).first()
    level = project_relation.level

    if not project_relation:
        return jsonify({'success': False, 'message': '没有此记录'})

    if not project_relation.parent_id:
        old_project = Project.query.filter_by(name=name).first()
        if old_project:
            return jsonify({'success': False, 'message': '名称已经存在'})

        project = Project.query.filter_by(name=project_relation.name).first()
        project.name = name
        db.session.add(project)

        # todo 删除文件
        delete_project_file(project)

    project_relation.name = name
    db.session.add(project_relation)
    db.session.commit()

    return jsonify(
        {'success': True, 'message': '更新成功', 'level': project_relation.level, 'parent_id': project_relation.parent_id})
