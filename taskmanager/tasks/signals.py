"""
Signals for the tasks app

Args:
    tasks (module): Django module

Returns:
    None

Raises:
    None 
"""

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Task
from .tasks import send_notification


@receiver(post_save, sender=Task)
def send_notification_on_new_task(instance, created, **_kwargs):
    """
    Send notification to users when a new task is created

    Args:
        instance (Task): Task instance
        created (bool): Whether the instance was created or not
    """
    if created:
        subject = "New task assigned"
        message = f"You have been assigned to the task {instance.name}"
        for user in instance.assigned.all():
            expo_push_token = user.profile.expo_push_token
            if expo_push_token:
                send_notification.delay(subject, message, user.expo_push_token)
