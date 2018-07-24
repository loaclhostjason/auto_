from functools import wraps
from flask import g, abort
from flask import make_response
from flask_login import current_user


def after_this_request(f):
    if not hasattr(g, 'after_request_callbacks'):
        g.after_request_callbacks = []
    g.after_request_callbacks.append(f)
    return f


def allow_cross(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        r = make_response(func(*args, **kwargs))
        r.headers['Access-Control-Allow-Origin'] = '*'
        r.headers['Access-Control-Allow-Methods'] = 'HEAD, OPTIONS, GET, POST, DELETE, PUT'
        allow_headers = "Referer, Accept, Origin, User-Agent, X-Requested-With, Content-Type"
        r.headers['Access-Control-Allow-Headers'] = allow_headers
        return r

    return wrapper_func


def role_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)

    return decorated_function


def role_required2(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(403)
        if not current_user.is_admin and not current_user.is_pm_admin:
            abort(403)
        return f(*args, **kwargs)

    return decorated_function
