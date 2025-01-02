import logging
import random
import string
from argparse import ArgumentError

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError, transaction
from faker import Faker

User = get_user_model()

logger = logging.getLogger(__name__)
faker = Faker()


def generate_random_string(length=10):
    characters = string.ascii_letters + string.digits  # Letters and digits
    random_string = "".join(random.choice(characters) for _ in range(length))
    return random_string


class Command(BaseCommand):
    help = "Populate the database with sample data"

    def add_arguments(self, parser):
        parser.add_argument("count", type=int, help="The number of users to create")

    @transaction.atomic
    def handle(self, *args, **options):
        try:
            for _ in range(options["count"]):
                random_string = generate_random_string(10)
                User.objects.create(
                    username=f"{faker.name()}_{random_string}",
                    password=faker.password(),
                )

            logger.info("Created all users")
            self.stdout.write(self.style.SUCCESS("Successfully created all users"))
        except IntegrityError:
            raise CommandError("Failed to create all users due to IntegrityError")
        except ValidationError:
            raise CommandError("Failed to create all users due to ValidationError")
        except CommandError:
            raise CommandError("Failed to create all users due to CommandError")
        except ArgumentError:
            raise CommandError("Failed to create all users due to ArgumentError")
        except Exception:
            raise CommandError("Failed to create all users due to unexpected error")
