from celery import Celery
import os

# Create the Celery app instance
celery_app = Celery(
    'tasks',
    broker=os.environ.get('CELERY_BROKER_URL', 'redis://redis:6379/0'),
    backend=os.environ.get('CELERY_RESULT_BACKEND', 'redis://redis:6379/1'),
    include=['app.workers.tasks'] # Tell Celery where to find the tasks module
)

# Optional configuration
celery_app.conf.update(
    task_track_started=True,
)