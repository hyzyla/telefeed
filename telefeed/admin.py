from flask import url_for, redirect, request, abort
from flask_admin import Admin
from flask_admin.contrib import sqla
from flask_login import current_user

from . import models, db, app


class AdminModelView(sqla.ModelView):
    def is_accessible(self):
        return (
            current_user.is_active and
            current_user.is_authenticated and
            current_user.has_role('superuser')
        )

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))


admin = Admin(app, url='/', name='Telefeed', template_mode='bootstrap3')

admin.add_view(AdminModelView(models.Post, db.session))
admin.add_view(AdminModelView(models.Feed, db.session))
admin.add_view(AdminModelView(models.Role, db.session))
admin.add_view(AdminModelView(models.User, db.session))
