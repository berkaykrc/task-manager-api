from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Task
from .tasks import send_notification

@receiver(post_save, sender=Task)
def send_notification_on_new_task(instance, created, **kwargs):
    if created:
        subject = 'New task assigned'
        message = f'You have been assigned to the task {instance.title}'
        for user in instance.assigned.all():
            expo_push_token = user.profile.expo_push_token
            if expo_push_token:
                send_notification.delay(subject, message, user.expo_push_token)