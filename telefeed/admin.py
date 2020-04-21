from flask import url_for, redirect, request, abort
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib import sqla
from flask_login import current_user

from . import models, db, app, tasks


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


class TaskView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/tasks.html', tasks=tasks.worker.tasks)


class PostModelView(AdminModelView):
    column_searchable_list = ('title', 'body', 'link')


class FeedModelView(AdminModelView):
    column_searchable_list = ('name', 'url')


admin = Admin(app, url='/', name='Telefeed', template_mode='bootstrap3')

admin.add_view(TaskView(name='Tasks', endpoint='tasks'))
admin.add_view(PostModelView(models.Post, db.session))
admin.add_view(FeedModelView(models.Feed, db.session))
admin.add_view(AdminModelView(models.Role, db.session))
admin.add_view(AdminModelView(models.User, db.session))
admin.add_view(AdminModelView(models.Channel, db.session))
