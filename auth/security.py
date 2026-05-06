from flask import session, redirect
from functools import wraps

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return wrapper


def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if "role" not in session:
                return redirect("/login")

            if session["role"] not in allowed_roles:
                return "Access Denied (Role Restriction)"

            return f(*args, **kwargs)
        return wrapper
    return decorator