from celery import Celery

app = Celery('tasks', broker='redis://redis:6379/0')
app.conf.result_backend = 'redis://redis:6379/0'

import tasks

app.conf.beat_schedule = {
    'delete-unverified-users-daily': {
        'task': 'tasks.delete_unverified_users',
        'schedule': 60 * 60 * 24,  # каждый день (каждые 24 часа)
    },
}
