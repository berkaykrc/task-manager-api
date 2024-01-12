from exponent_server_sdk import PushClient, PushMessage
from django.core.management import call_command
from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_notification(subject, message, expo_push_token):
    try:
        logger.info('Sending notification to %s' % expo_push_token)
        response = PushClient().publish(
            PushMessage(to=expo_push_token,
                        body=message,
                        title=subject))
        logger.info(f'"{response}" sent to {expo_push_token}')
    except Exception as e:
        logger.error('Error sending notification: %s' % str(e))
        raise e


@shared_task
def task_send_fcm_notifications():
    call_command('send_fcm_notifications')
