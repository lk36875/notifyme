from celery import Celery, Task
from flask import Flask


def celery_create_app() -> Celery:
    """Initialize a Celery application, set the timezone and return the application."""
    celery_app = Celery('celery-notify_me')
    celery_app.conf.timezone = 'Europe/Warsaw'  # type: ignore
    celery_app.set_default()
    return celery_app


def celery_init_app(celery_app: Celery, app: Flask) -> Celery:
    """Adapting Celery to Flask factory pattern."""
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app.Task = FlaskTask
    celery_app.config_from_object(app.config["CELERY"])
    app.extensions["celery"] = celery_app
    return celery_app
