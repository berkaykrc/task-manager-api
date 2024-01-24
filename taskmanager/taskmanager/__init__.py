"""
This module initializes the task manager API.

It imports the Celery app from the celery module and exposes it as celery_app.
"""
from .celery import app as celery_app

__all__ = ("celery_app",)
