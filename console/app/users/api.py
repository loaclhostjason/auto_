from flask_login import login_required
from flask import jsonify, request

from . import users
from .forms import UserForm
from ..base import Check
from ..models import User
from .. import db
from ..decorators import role_required


def validate_user_pwd(upw, upw2):
    if upw != upw2:
        result = '密码不一致'
        return result
    return


@users.route('/info/<int:id>')
@login_required
@role_required
def get_user_info(id):
    user = User.query.filter_by(id=id).first()
    if not user:
        return jsonify({'success': False, 'message': '没有用户记录'})
    return jsonify({'success': True, 'data': user.to_dict()})


@users.route('/create', methods=['POST'])
@login_required
@role_required
def create_users():
    users_params = request.form.to_dict()

    form = UserForm()
    error_message = Check(form).get_error_message()
    if error_message:
        return jsonify({'success': False, 'message': str(error_message)})

    upw_message = validate_user_pwd(users_params['upw'], users_params['upw2'])
    if upw_message:
        return jsonify({'success': False, 'message': upw_message})

    old_user = User.query.filter_by(username=users_params['username']).first()
    if old_user:
        return jsonify({'success': False, 'message': '用户名重复'})

    add_user_dict = form.get_user_form()
    user = User(**add_user_dict)
    db.session.add(user)
    return jsonify({'success': True, 'message': '创建用户成功'})


@users.route('/edit/<int:id>', methods=['POST'])
@login_required
@role_required
def edit_users(id):
    users_params = request.form.to_dict()
    type = request.args.get('type')

    user = User.query.filter_by(id=id).first()
    if not user:
        return jsonify({'success': False, 'message': '没有记录'})

    if not type:
        user_message = UserForm().validate_user_info()
        if user_message:
            return jsonify({'success': False, 'message': user_message})

        old_user = User.query.filter_by(username=users_params['username']).first()
        if old_user:
            return jsonify({'success': False, 'message': '用户名重复了'})

        users_params['expiry_time'] = '{} {}'.format(users_params['expiry_time'], '23:59:59')

    else:
        user_message = UserForm().validate_user_pwd()
        if user_message:
            return jsonify({'success': False, 'message': user_message})
        error_message = validate_user_pwd(users_params['upw'], users_params['upw2'])
        if error_message:
            return jsonify({'success': False, 'message': error_message})

    User.update_model(user, users_params)
    return jsonify({'success': True, 'message': '更新成功'})


@users.route('/delete/<int:id>', methods=['POST'])
@login_required
@role_required
def delete_user(id):
    user = User.query.filter_by(id=id).first()
    if not user:
        return jsonify({'success': False, 'message': '没有用户记录'})

    db.session.delete(user)
    return jsonify({'success': True, 'message': '删除成功'})
