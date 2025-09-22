import os
# This file centralizes Celery configuration
# It is only read by the Celery worker, not the API

broker_url = os.environ.get('CELERY_BROKER_URL', 'redis://redis:6379/0')
result_backend = os.environ.get('CELERY_RESULT_BACKEND', 'redis://redis:6379/1')

# Define the queue and task routing
task_queues = {
    'analysis': {
        'exchange': 'analysis',
        'routing_key': 'analysis',
    },
}
task_routes = {
    'app.workers.tasks.analyze_comment_async': {'queue': 'analysis'},
}