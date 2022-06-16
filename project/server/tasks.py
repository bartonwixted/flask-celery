import os
import time
from celery import Celery
from project.server.main import lolscrape


celery = Celery(__name__)
celery.conf.broker_url = os.environ.get(
    "CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.environ.get(
    "CELERY_RESULT_BACKEND", "redis://localhost:6379")


@celery.task(name="create_task")
def create_task(task_type):
    for i in range(int(task_type)*10):
        print("poo")
        time.sleep(1)
    return True


@celery.task(name="background_scrape")
def background_scrape(gameID):
    gamedata = lolscrape.pull_game_data(gameID)
    return gamedata
