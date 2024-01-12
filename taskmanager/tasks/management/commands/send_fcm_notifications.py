from django.core.management.base import BaseCommand
from django.utils import timezone
from tasks.models import Task
from tasks.tasks import send_notification


class Command(BaseCommand):
    help = 'Send notifications to frontend using Firebase Cloud Messaging'

    def handle(self, *args, **options):
        new_tasks = self.get_new_tasks()
        for task in new_tasks:
            self.send_task_notifications(task)

    def get_new_tasks(self):
        one_day_ago = timezone.now() - timezone.timedelta(days=1)
        return Task.objects.filter(created_at__gte=one_day_ago)

    def send_task_notifications(self, task):
        subject = 'New task created'
        message = f'New task {task.name} created'
        for user in task.assigned.all():
            expo_push_token = user.profile.expo_push_token
            if expo_push_token:
                send_notification.delay(subject, message, expo_push_token)
