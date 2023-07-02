# type: ignore
import os
from datetime import datetime

import pytz
from celery import shared_task
from celery.schedules import crontab

from notify.app.logger import LoggerType, create_logger
from notify.models.query_params import Frequency

from .init_celery import celery_create_app
from .setup_scheduled_events import setup_scheduled_events

logger = create_logger(LoggerType.CELERY, "SCHEDULER")

celery_app = celery_create_app()


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """
    Sets up periodic tasks for the NotifyMe API.

    This function is called after the Celery app is configured and sets up periodic tasks for the API
    using the `add_periodic_task` method. The tasks are defined in the `create_periodic_tasks` function.
    """
    output_message.delay("Starting scheduler.")

    for tasks in create_periodic_tasks():
        sender.add_periodic_task(tasks["crontab"], tasks["task"], name=tasks["name"])


@celery_app.task()
def run_periodic_send(frequency_str: str):
    """
    Runs a periodic task to send weather reports to users.

    This function is called by the Celery app to send weather reports to users on a periodic basis.
    The frequency of the reports is determined by the `frequency_str` argument.

    Args:
        frequency_str: A string indicating the frequency of the weather reports ("day" or "hour").
    """
    from .make_celery import flask_app

    with flask_app.app_context():
        if frequency_str.lower() == "day":
            frequency = Frequency.DAY
        else:
            frequency = Frequency.HOUR
        service = setup_scheduled_events(frequency)
        service.run()


@shared_task(ignore_result=False)
def output_message(message: str) -> str:
    return message


def create_periodic_tasks():
    """
    Creates periodic tasks for the NotifyMe API.

    This function creates periodic tasks for the API using the `create_tasks` or `create_test_tasks` functions,
    depending on whether the `CELERY_TEST` environment variable is set.

    Yields:
        A dictionary containing the crontab schedule, task function, and task name for each periodic task.
    """
    test_env = os.environ.get("CELERY_TEST", False)
    if test_env:
        tasks = create_test_tasks()
    else:
        tasks = create_tasks()

    for task in tasks:
        yield task


def create_tasks():
    """
    Creates production periodic tasks for the NotifyMe API.

    This function creates periodic tasks for the API that are used in production.
    The tasks include sending weather reports to users on a daily and hourly basis.

    Returns:
        A list of dictionaries containing the crontab schedule, task function, and task name for each periodic task.
    """
    return [
        {
            "crontab": crontab(hour=6, minute=10, day_of_week=1),
            "task": run_periodic_send.s("DAY"),
            "name": "Send mail for 7 day weather report every Monday at 6:10",
        },
        {
            "crontab": crontab(hour=6),
            "task": run_periodic_send.s("HOUR"),
            "name": "Send mail for 24 hour weather report every day at 6:00",
        },
    ]


def create_test_tasks():
    """
    Creates test periodic tasks for the NotifyMe API.

    This function creates periodic tasks for the API that are used in testing. 
    The tasks include outputting a test message every 10 seconds, sending weather reports to users every 30 seconds.

    Returns:
        A list of dictionaries containing the crontab schedule, task function, and task name for each periodic task.
    """
    tz = pytz.timezone("Europe/Warsaw")
    hour, minute, day_of_week = datetime.now(tz).hour, datetime.now(tz).minute, datetime.now(tz).weekday() + 1
    return [
        {
            "crontab": 10.0,
            "task": output_message.s(f"TEST,  {hour}, {minute + 1}, {day_of_week}"),
            "name": "add every 10",
        },
        {
            "crontab": 30.0,
            "task": run_periodic_send.s("DAY"),
            "name": "Send mail for 7 day weather report every Monday at 6:10",
        },
        {
            "crontab": 30.0,
            "task": run_periodic_send.s("HOUR"),
            "name": "Send mail for 24 hour weather report every day at 6:00",
        },
    ]
