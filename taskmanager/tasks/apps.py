"""
Tasks app config

Attributes:
    default_auto_field (str): Default auto field
    name (str): App name

"""
from django.apps import AppConfig


class TasksConfig(AppConfig):
    """
    Tasks app config

    Args:
        AppConfig (AppConfig): Django AppConfig class
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "tasks"

    def ready(self):
        """
        Method called when the app is ready

        Returns:
            None
        """
        import tasks.signals
