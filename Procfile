release: flask db upgrade
web: gunicorn app:app
worker: celery worker --app=telefeed.tasks.worker