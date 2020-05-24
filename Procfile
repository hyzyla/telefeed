release: flask db upgrade
web: gunicorn app:app
worker: dramatiq --processes 1 --threads 8 telefeed.tasks