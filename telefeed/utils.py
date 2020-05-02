from flask import url_for, redirect, request, abort
from flask_login import current_user


def is_user_admin() -> bool:
    return (
        current_user.is_active and
        current_user.is_authenticated and
        current_user.has_role('superuser')
    )


def validate_user_admin():
    if not is_user_admin():
        if current_user.is_authenticated:
            # permission denied
            abort(403)
        else:
            # login
            return redirect(url_for('security.login', next=request.url))