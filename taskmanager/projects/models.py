"""
This module contains the Project model for the task manager API.

The Project model represents a project in the task manager.
It has attributes such as name, description, start_date, end_date, and users.
It also includes validation functions for start_date and end_date.
"""

from typing import TYPE_CHECKING, Any

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

if TYPE_CHECKING:
    from django.contrib.auth.models import User


def validate_start_date(value):
    """
    Validates that the provided start date is not in the past.

    Args:
        value (datetime): The start date to validate.

    Raises:
        ValidationError: If the start date is in the past.
    """
    if value < timezone.now():
        raise ValidationError("Start date cannot be in the past.")


def validate_end_date(value):
    """
    Validates that the provided end date is not in the past.

    Args:
        value (datetime): The end date to validate.

    Raises:
        ValidationError: If the end date is in the past.
    """
    if value < timezone.now() and value:
        raise ValidationError("End date cannot be in the past.")


class Project(models.Model):
    """
    Represents a project in the task manager.

    Attributes:
        name (str): The name of the project.
        description (str): The description of the project.
        start_date (datetime): The start date of the project.
        end_date (datetime): The end date of the project.
        users (ManyToManyField): The users associated with the project.
    """

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_date = models.DateTimeField(validators=[validate_start_date])
    end_date = models.DateTimeField(validators=[validate_end_date])
    users: "models.ManyToManyField[User, Any]" = models.ManyToManyField(
        get_user_model(), related_name="projects", blank=True
    )
    owner = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        related_name="owned_projects",
        null=True,
    )

    def __str__(self):
        return f"{self.name}"

    class Meta:
        ordering = ["-start_date"]
        verbose_name = "Project"
        verbose_name_plural = "Projects"
        constraints = [
            models.CheckConstraint(
                check=models.Q(start_date__lte=models.F("end_date")),
                name="project_start_date_lte_end_date",
                violation_error_message="Start date must be less than or equal to end date.",
            ),
            models.CheckConstraint(
                check=models.Q(end_date__gte=models.F("start_date")),
                name="project_end_date_gte_start_date",
                violation_error_message="End date must be greater than or equal to start date.",
            ),
        ]
