"""
This file is used to create celery worker and celery beat.
"""
from notify.app.app import create_app

flask_app = create_app()
celery_app = flask_app.extensions["celery"]
