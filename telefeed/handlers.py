from werkzeug.exceptions import abort

from . import app, tasks
from telefeed.utils import validate_user_admin


@app.route('/tasks/<name>/execution', methods=['POST'])
def run_task(name: str):
    validate_user_admin()
    if not name.startswith('telefeed.tasks'):
        raise abort(400)
    tasks.worker.tasks[name].delay()
    return name
