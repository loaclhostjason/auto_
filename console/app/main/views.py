# coding: utf-8
from flask import render_template, redirect, url_for, jsonify, abort, request, flash, current_app
from flask_login import login_required

from . import main
from .forms import *
from ..base import Check
from ..app import upload_files
from config import Config
import os
from datetime import datetime
from .models import *
from collections import defaultdict


@main.route('/', methods=['GET', 'POST'])
@main.route('/projects', methods=['GET', 'POST'])
@login_required
def projects():
    projects = Project.query.order_by(Project.id).all()
    return render_template('main/projects.html', projects=projects)


def get_project_children(project_id):
    result = list()
    first_relation = ProjectRelation.query.filter_by(project_id=project_id, level=1).first()
    d = {
        'level_1': first_relation.name,
    }

    second_relation = ProjectRelation.query.filter_by(parent_id=first_relation.id, level=2).all()
    if not second_relation:
        return result

    for v in second_relation:
        d['level_2'] = v.name

        third_relation = ProjectRelation.query.filter_by(parent_id=v.id, level=3).all()
        if third_relation:
            for th in third_relation:
                d['level_3'] = th.name

                forth_relation = ProjectRelation.query.filter_by(parent_id=th.id, level=4).all()
                if forth_relation:
                    for forth in forth_relation:
                        # d['level_4'] = forth.name
                        # print(forth.name)
                        d.update({'level_4': forth.name})
                        result.append(d.copy())

    return result


@main.route('/project/data/edit/<int:project_id>', methods=['GET', 'POST'])
@login_required
def edit_project_data(project_id):
    project = Project.query.get_or_404(project_id)

    result = get_project_children(project_id)
    # max_len = max([len(v) for v in result.values()])
    print(result)
    return render_template('main/edit_project_data.html', project=project, result=result)


@main.route('/project/create_edit', methods=['GET', 'POST'])
@login_required
def create_edit_project():
    return render_template('main/create_edit_project.html')


@main.route('/project/edit/<int:project_id>', methods=['GET', 'POST'])
@login_required
def edit_file(project_id):
    project = Project.query.get_or_404(project_id)
    return render_template('main/create_edit_project.html', project=project)
