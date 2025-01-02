# ruff: noqa: F403
import os

SETTINGS_MODULE = os.getenv("DJANGO_SETTINGS_MODULE", "taskmanager.settings.local")

if SETTINGS_MODULE == "taskmanager.settings.production":
    from .production import *
else:
    from .local import *
