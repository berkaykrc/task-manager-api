"""
Profiles app.

This file contains the Profiles app configuration.
"""
from django.apps import AppConfig


class ProfilesConfig(AppConfig):
    """
    Profiles app configuration.

    This class contains the Profiles app configuration.

    Attributes:
        default_auto_field (str): The default auto field.
        name (str): The app name.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "profiles"
