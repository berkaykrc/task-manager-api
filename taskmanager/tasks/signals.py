"""
Signals for the tasks app

This module contains signal handlers for the tasks app in a Django project.
Signals are used to perform certain actions when certain events occur in the application,
such as when a new task is created or when a user is mentioned in a task.

Attributes:
    tasks (module): The Django module for tasks

Returns:
    None

Raises:
    None
"""

from django.db.models.signals import post_save
from django.dispatch import receiver

from tasks.tasks import send_notification

from .models import Mention, Task


@receiver(post_save, sender=Task)
def send_notification_on_new_task(instance, created, **_kwargs):
    """
    Send notification to users when a new task is created

    Args:
        instance (Task): The Task instance that was saved
        created (bool): Whether the instance was created or not
    """
    if created:
        subject = "New task assigned"
        message = f"You have been assigned to the task {instance.name}"
        for user in instance.assigned.all():
            expo_push_token = user.profile.expo_push_token
            if expo_push_token:
                send_notification.delay(subject, message, user.expo_push_token)


@receiver(post_save, sender=Mention)
def send_notification_on_mention(instance, created, **_kwargs):
    """
    Send notification to users when they are mentioned in a task

    Args:
        instance (Mention): Mention instance
        created (bool): Whether the instance was created or not
    """
    if created:
        subject = "You have been mentioned"
        message = f"You have been mentioned in the task {instance.comment.task.name}"
        user = instance.mentioned_user
        if user.profile.expo_push_token:
            send_notification.delay(subject, message, user.profile.expo_push_token)
