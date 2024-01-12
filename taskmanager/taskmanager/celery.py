import os
import environ
from celery import Celery
from celery.schedules import crontab

env = environ.Env()
environ.Env.read_env()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskmanager.settings')

app = Celery('taskmanager', backend=env('REDIS_URL'), broker=env('REDIS_URL'))
print(env('REDIS_URL'))
print(app)
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.broker_connection_retry_on_startup = True


app.conf.beat_schedule = {
    'run-your-command-every-midnight': {
        'task': 'tasks.tasks.task_send_fcm_notifications',
        'schedule': crontab(minute=0, hour=0),
    },
}
