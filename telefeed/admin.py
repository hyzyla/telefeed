from flask_admin import Admin, BaseView, expose
from flask_admin.contrib import sqla

from telefeed.utils import is_user_admin, validate_user_admin
from . import app, db, models, tasks


class AdminModelView(sqla.ModelView):
    def is_accessible(self):
        return is_user_admin()

    def _handle_view(self, name, **kwargs):
        validate_user_admin()


class AdminView(BaseView):
    def is_accessible(self):
        return is_user_admin()


class TaskView(AdminView):

    @expose('/')
    def index(self):
        _tasks = [
            task
            for task in tasks.worker.tasks.values()
            if task.name.startswith('telefeed')
        ]
        return self.render('admin/tasks.html', tasks=_tasks)


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
