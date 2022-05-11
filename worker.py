import os

from celery import Celery

from selenium_twitter import main

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")


@celery.task()
def twitter(search, filename, step):
    main(search, filename, step)
