from functools import wraps
from flask import abort
from flask_login import current_user

def role_required(role):
    def _decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(403)
            if getattr(current_user, 'role', None) != role:
                abort(403)
            return f(*args, **kwargs)
        return wrapper
    return _decorator

def admin_required(f):
    return role_required('admin')(f)

def prestador_required(f):
    return role_required('prestador')(f)