from celery import Celery
import os

celery_app = Celery('tasks')

# Use a config file to avoid import-time evaluation
celery_app.config_from_object('app.celeryconfig')

# Tell Celery where to find tasks
celery_app.autodiscover_tasks(['app.workers'])