"""
This module defines the models and validation functions for handling shared files
in the task manager application. It includes validation for file extensions, content,
and size to ensure that only appropriate files are uploaded.
"""

from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files import File
from django.db import models
from projects.models import Project
from tasks.models import Task

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


def validate_file_extension_and_content(value: File):
    """
    Validates the file extension and content of the uploaded file.

    Args:
        value (File): The uploaded file.

    Raises:
        ValidationError: If the file extension or content is not allowed.
    """
    if not isinstance(value.name, str):
        raise ValidationError("Invalid file name.")
    ext = Path(value.name).suffix
    valid_extensions = [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".txt"]
    if ext.lower() not in valid_extensions:
        raise ValidationError(
            f'Unsupported file extension. Allowed extensions are: {", ".join(valid_extensions)}.'
        )

    valid_content_types = {
        b"%PDF": "application/pdf",
        b"\xd0\xcf\x11\xe0": "application/msword",
        b"PK\x03\x04": "application/vnd.openxmlformats-officedocument",
        b"\x0a\x00\x00": "application/vnd.ms-excel",
    }

    # Read the first few bytes of the file
    file_head = value.read(4)
    value.seek(0)  # Reset file pointer

    # Check if the file header matches any of the valid content types
    content_type = next(
        (ct for key, ct in valid_content_types.items() if file_head.startswith(key)),
        None,
    )

    if content_type is None and ext != ".txt":  # Special case for .txt files
        raise ValidationError("Unsupported file type.")


def validate_file_size(value: File):
    """
    Validates the size of the uploaded file.

    Args:
        value (File): The uploaded file.

    Raises:
        ValidationError: If the file size exceeds the limit.
    """
    if value.size > MAX_FILE_SIZE:
        raise ValidationError(f"File size should not exceed {MAX_FILE_SIZE} MB.")


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

    file = models.FileField(
        upload_to="shared_files/",
        validators=[validate_file_extension_and_content, validate_file_size],
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="shared_files"
    )
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="shared_files",
    )

    def __str__(self) -> str:
        return self.file.name
