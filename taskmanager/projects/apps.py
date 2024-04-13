"""
App configuration for the 'projects' app.
"""
from django.apps import AppConfig


class ProjectsConfig(AppConfig):
    """
    AppConfig class for the 'projects' app.

    This class represents the configuration for the 'projects' app in the Django project.
    It sets the default auto field and the name of the app.

    Attributes:
        default_auto_field (str): The default auto field to use for models in the app.
        name (str): The name of the app.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'projects'
