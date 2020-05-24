from . import app, tasks
from telefeed.utils import validate_user_admin
from dramatiq import Actor


@app.route('/tasks/parse_feeds/execution', methods=['GET'])
def run_parsing():
    actor: Actor = tasks.broker.actors['parse_feeds']
    actor.send()
    return 'OK'


@app.route('/tasks/<name>/execution', methods=['POST'])
def run_task(name: str):
    validate_user_admin()

    actor: Actor = tasks.broker.actors[name]
    actor.send()
    return name
