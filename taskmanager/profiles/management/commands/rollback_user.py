from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = "Rollback users created by populate_db command"

    def handle(self, *_args, **_kwargs):
        users = User.objects.filter(username__contains="_")
        user_count = users.count()
        users.delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {user_count} users"))
