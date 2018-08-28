# coding: utf-8
from flask import render_template, redirect, url_for, jsonify, abort, request, flash, current_app
from flask_login import login_required, current_user

from . import main
from .forms import *
from ..base import Check
from ..app import upload_files
from console.config import Config
import os
from datetime import datetime
from .models import *
from collections import defaultdict
from .func import *
from ..models import User
from sqlalchemy import or_, func

import json
from console.util import ExportXml
from console.export_json import ExportJson
from ..manage.models import Attr, ExtraAttrContent
from .func_extra import *
from ..manage.models import ExtraAttrData
import time
from console.import_json import ImportJson


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
    project_relation_id = request.args.get('project_relation_id') or 0
    attr = Attr.query.filter_by(level=level).first()
    extra_attr = attr.extra_attr_content

    # todo
    extra_data = ExtraAttrData.query.filter_by(project_id=project_id, project_relation_id=project_relation_id).first()
    if not attr or not extra_attr:
        abort(404)

    if request.method == 'POST':

        if int(level) == 1:
            pin_num = request.form.get('pin_num')
            pin = get_extra_content()
            pin.append({'pin_num': pin_num})

            reset_sec = get_extra_section_content()

            d = {
                'level': 1,
                'project_id': project_id,
                'project_relation_id': project_relation_id,
                'pin': json.dumps(pin),
                'reset_sec': json.dumps(reset_sec),
            }
            ExtraAttrData.create_edit(d, project_id, project_relation_id)

        else:
            # name = request.args.get('name')
            is_open_reset = request.form.get('reset_section')
            content = get_extra_content2(project_id)

            d = {
                'level': 2,
                'project_id': project_id,
                'project_relation_id': project_relation_id,
                'is_open_reset': bool(is_open_reset == 'y'),
                'read_sec': json.dumps(content['readsection']),
                'write_sec': json.dumps(content['writsection']),
            }
            ExtraAttrData.create_edit(d, project_id, project_relation_id)

        flash({'success': '更新成功'})
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
                               extra_data=extra_data,
                               default_attr=default_attr, default_sec=default_sec)
    else:
        return render_template('main/create_edit_extra_attr_file2.html', project=project, extra_attr=extra_attr,
                               extra_data=extra_data,
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

    file = '{}_{}'.format(project.project_group.name, project.name)

    filename = '%s.95' % file
    filename_path = os.path.join(current_app.config['FILE_PATH'], filename)
    return download_files(filename_path, filename)


@main.route('/download_json')
@login_required
def download_json():
    project_id = request.args.get('project_id')
    project = Project.query.get_or_404(project_id)
    export_json = ExportJson(project_id)
    export_json.run()

    file = '[{}]{}_{}'.format(project_id, project.project_group.name, project.name)
    filename = '%s.json' % file
    filename_path = os.path.join(current_app.config['JSON_FILE_PATH'], filename)
    return download_files(filename_path, filename)


@main.after_request
def after_request(response):
    if request.url_rule.rule in ['/download_file', '/download_json']:
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
    # level = project_relation.level
    project_group = project_relation.project.project_group_id if project_relation and project_relation.project else 0

    if not project_relation:
        return jsonify({'success': False, 'message': '没有此记录'})

    if not project_relation.parent_id:
        old_project = Project.query.filter_by(name=name, project_group_id=project_group).first()
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


JSON = ['json']


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in JSON


@main.route('/import/json', methods=['POST'])
@login_required
def import_json():
    file = request.files['json_file']
    if not file or not allowed_file(file.filename):
        return jsonify({'success': False, 'message': '格式不对'})

    data = file.stream.read().decode('utf-8')
    data = json.loads(data or '{}')
    if not data:
        return jsonify({'success': False, 'message': '文件没有数据'})

    project = data['project']
    project_relation = data['project_relation']
    name = '{}_{}'.format(project['name'], int(time.time()))
    project['user_id'] = current_user.id
    project['name'] = name

    new_project = Project(**project)
    db.session.add(new_project)
    db.session.flush()

    project_id = new_project.id
    _json = ImportJson(name, project_id, project_relation)
    _json.run()
    return jsonify({'success': True, 'message': '上传成功', 'project_id': project_id})
