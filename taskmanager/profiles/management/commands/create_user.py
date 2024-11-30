# your_app/management/commands/populate_data.py

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

# import ipdb
# ipdb.set_trace()

#fixme: fix profile model update issue
#from taskmanager.profiles.models import Profile

from faker import Faker

import logging
import random
import string

from datetime import datetime
User = get_user_model()

logger = logging.getLogger(__name__)
logger = logging.getLogger('tasks')
faker = Faker()


def generate_random_string(length=10):
    characters = string.ascii_letters + string.digits  # Letters and digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string

from django.db.models.signals import post_save


class Command(BaseCommand):
    help = 'Populate the database with sample data'

    def handle(self, *args, **kwargs):
        users = []
        # profiles = []
        for i in range(100):
            random_string = generate_random_string(10)
            user = (User(username=f"{faker.name()}_{random_string}", password=faker.password()))
            users.append(user)
            # profile = (Profile(user=user))
            # profiles.append(profile)
        User.objects.bulk_create(users)
        # Profile.objects.bulk_create(profiles)

        for user in users:
            post_save.send(sender=User, instance=user, created=True)

        logger.info("Created all users")




