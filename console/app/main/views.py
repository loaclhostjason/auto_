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

import json
from util import ExportXml


@main.route('/', methods=['GET', 'POST'])
@main.route('/projects', methods=['GET', 'POST'])
@login_required
def projects():
    project_query = Project.query.order_by(Project.id)
    if current_user.is_admin:
        projects = project_query.all()
    else:
        projects = Project.query.filter_by(user_id=current_user.id).all()
    return render_template('main/projects.html', projects=projects)


@main.route('/project/data/edit/<int:project_id>', methods=['GET', 'POST'])
@login_required
def edit_project_data(project_id):
    project = Project.query.get_or_404(project_id)

    if request.method == 'POST':
        data = ProjectData.get_content(project_id)
        if not data:
            return redirect(request.url)

        new_dict = dict()
        for v in data:
            new_dict[v['project_relation_id']] = v

        for project_relation_id, val in new_dict.items():
            val['content'] = json.dumps(val['content'])
            old_project_data = ProjectData.query.filter_by(project_relation_id=project_relation_id).first()
            if old_project_data:

                ProjectData.update_model(old_project_data, val)
            else:
                new_project_data = ProjectData(**val)
                db.session.add(new_project_data)

        ProjectData.update_real_content(project_id)
        flash({'success': '更新成功'})
        export_xml = ExportXml(project_id)
        export_xml.run()
        return redirect(request.url)

    result = get_project_children(project_id)
    # max_len = max([len(v) for v in result.values()])
    project_data = ProjectData.query.filter_by(project_id=project_id).all()
    project_data = {v.project_relation_id: v.to_dict() for v in project_data}
    return render_template('main/edit_project_data.html', project=project, result=result, project_data=project_data)


@main.route('/project/create_edit', methods=['GET', 'POST'])
@login_required
def create_edit_project():
    return render_template('main/create_edit_project.html')


@main.route('/project/edit/<int:project_id>', methods=['GET', 'POST'])
@login_required
def edit_file(project_id):
    project = Project.query.get_or_404(project_id)
    return render_template('main/create_edit_project.html', project=project)


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
    file_name = request.args.get('file_name')
    return download_files(file_name)


@main.route('/project/edit/name', methods=['POST'])
@login_required
def edit_project_name():
    name = request.form.get('name')
    id = request.form.get('id')
    if not name:
        return jsonify({'success': False, 'message': '名称不能为空'})

    project_relation = ProjectRelation.query.filter_by(id=id).first()
    if not project_relation:
        return jsonify({'success': False, 'message': '没有此记录'})

    if not project_relation.parent_id:
        old_project = Project.query.filter_by(name=name).first()
        if old_project:
            return jsonify({'success': False, 'message': '名称已经存在'})

        project = Project.query.filter_by(name=project_relation.name).first()
        project.name = name
        db.session.add(project)

    project_relation.name = name
    db.session.add(project_relation)

    print('level', project_relation.level)
    return jsonify(
        {'success': True, 'message': '更新成功', 'level': project_relation.level, 'parent_id': project_relation.parent_id})
