"""
This module contains the model definitions for the SharedFile model.
"""

from django.contrib.auth import get_user_model
from django.db import models


class SharedFile(models.Model):
    """
    Represents a shared file in the system.

    Attributes:
        file (FileField): The uploaded file.
        uploaded_at (DateTimeField): The timestamp when the file was uploaded.
        uploaded_by (ForeignKey): The user who uploaded the file.
        project (ForeignKey): The project associated with the file.
        task (ForeignKey): The task associated with the file (optional).
    """
    file = models.FileField(upload_to='shared_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE)
    task = models.ForeignKey(
        'tasks.Task', on_delete=models.CASCADE, null=True, blank=True)
