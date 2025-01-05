"""
This module contains tasks related to sending notifications.

Tasks:
- send_notification: Sends a notification to the specified Expo push token.
- send_due_date_notifications: Sends notifications to users with tasks due tomorrow.
- task_send_fcm_notifications: Executes the 'send_fcm_notifications' management command.
"""

import logging
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Optional

from celery import shared_task
from django.core.management import call_command
from exponent_server_sdk import PushClient, PushMessage

from .models import Task

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from profiles.models import Profile


@shared_task
def send_notification(subject: str, message: str, expo_push_token: str) -> None:
    """
    Sends a notification to the specified Expo push token.

    Args:
        subject (str): The subject of the notification.
        message (str): The body of the notification.
        expo_push_token (str): The Expo push token of the recipient.

    Raises:
        Exception: If there is an error sending the notification.
    """
    try:
        logger.info("Sending notification to %s", expo_push_token)
        response = PushClient().publish(
            PushMessage(
                to=expo_push_token,
                body=message,
                title=subject,
                data=None,
                sound=None,
                ttl=None,
                expiration=None,
                priority=None,
                badge=None,
                category=None,
                display_in_foreground=None,
                channel_id=None,
                subtitle=None,
                mutable_content=None,
            )
        )
        logger.info("%s sent to %s", response, expo_push_token)
    except Exception as e:
        logger.error("Error sending notification: %s", str(e))
        raise e


@shared_task
def send_due_date_notifications() -> None:
    """
    Sends notifications to users with tasks due tomorrow.

    This task sends a notification to users with tasks due tomorrow. The notification
    is sent to the Expo push token of each user.

    Raises:
        Exception: If there is an error sending the notification.

    """
    tasks = Task.objects.filter(
        end_date__date=datetime.now().date() + timedelta(days=1)
    )
    for task in tasks:
        subject = "Task due soon"
        message = f"The task {task.name} is due tomorrow"
        for user in task.assigned.all():
            # HACK it doesnt help to recognize the type of user.profile
            profile: Profile = user.profile
            expo_push_token: Optional[str] = getattr(profile, "expo_push_token", None)
            if expo_push_token:
                send_notification.delay(subject, message, expo_push_token)


@shared_task
def task_send_fcm_notifications():
    """
    Executes the 'send_fcm_notifications' management command.

    This task is responsible for sending FCM (Firebase Cloud Messaging) notifications
    using the Django management command 'send_fcm_notifications'.
    """
    call_command("send_fcm_notifications")
