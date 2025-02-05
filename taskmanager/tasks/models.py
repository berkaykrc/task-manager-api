"""
This module contains the models for the tasks app.

Classes:
    Task: A class that represents a task.
    Comment: A class that represents a comment.
    Mention: A class that represents a mention.

Functions:
    validate_start_date: A function that validates the start date of a task.
    validate_end_date: A function that validates the end date of a task.
"""

from datetime import datetime

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from projects.models import Project


def validate_start_date(value: datetime) -> None:
    """
    Function that validates the start date of a task.

    Args:
        value (datetime): The start date of the task.

    Raises:
        ValidationError: If the start date is in the past.
    """
    if value <= timezone.now():
        raise ValidationError("Start date cannot be in the past")


def validate_end_date(value: datetime) -> None:
    """
    Function that validates the end date of a task.

    Args:
        value (datetime): The end date of the task.

    Raises:
        ValidationError: If the end date is in the past.
    """
    if value <= timezone.now():
        raise ValidationError("End date cannot be in the past")


class Task(models.Model):
    """
    A class that represents a task.

    Attributes:
        name (CharField): The name of the task.
        created_at (DateTimeField): The date and time the task was created.
        start_date (DateTimeField): The date and time the task is scheduled to start.
        end_date (DateTimeField): The date and time the task is scheduled to end.
        description (TextField): The description of the task.
        priority (CharField): The priority of the task.
        status (CharField): The status of the task.
        assigned (ManyToManyField): The users assigned to the task.
        creator (ForeignKey): The user who created the task.
    """

    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)
    start_date = models.DateTimeField(
        validators=[
            validate_start_date,
        ]
    )
    end_date = models.DateTimeField(
        validators=[
            validate_end_date,
        ]
    )
    description = models.TextField()
    PRIORITY_CHOICES = [
        ("ASAP", "Asap"),
        ("MEDIUM", "Medium"),
        ("LOW", "Low"),
    ]
    priority = models.CharField(max_length=6, choices=PRIORITY_CHOICES, default="LOW")
    STATUS_CHOICES = [
        ("TODO", "To Do"),
        ("INPROGRESS", "In Progress"),
        ("DONE", "Done"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="TODO")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    assigned: models.ManyToManyField = models.ManyToManyField(
        get_user_model(), related_name="tasks"
    )
    creator = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="created_tasks"
    )

    class Meta:
        """
        Meta class that defines the constraints for the Task model.

        Attributes:
            constraints (list): A list of constraints for the Task model.
        """

        constraints = [
            models.CheckConstraint(
                check=models.Q(start_date__lte=models.F("end_date")),
                name="task_start_date_lte_end_date",
            ),
            models.CheckConstraint(
                check=models.Q(end_date__gte=models.F("start_date")),
                name="task_end_date_gte_start_date",
            ),
        ]

    @property
    @admin.display(
        boolean=True,
        ordering="start_date",
        description="Is the task overdue?",
    )
    def duration(self) -> str:
        """
        Calculates the duration of the task.

        Returns:
            str: The duration of the task in the format "Xh Ym"
                where X is the number of hours and Y is the number of minutes.

        Raises:
            ValueError: If the start_date and/or end_date is not set.
            ValueError: If the end_date is earlier than the start_date.
        """
        if self.start_date and self.end_date:
            duration = self.end_date - self.start_date
            if duration.total_seconds() <= 0:
                return "Error: End date is earlier than start date"
            total_seconds = int(duration.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            return f"{hours}h {minutes}m"
        return "Error: start_date and/or end_date is not set"

    def __str__(self) -> str:
        """
        Returns:
            str: The name of the task.
        """
        return str(self.name)


class Comment(models.Model):
    """
    A class that represents a comment.

    Attributes:
        task (ForeignKey): The task the comment is associated with.
        creator (ForeignKey): The user who created the comment.
        created_at (DateTimeField): The date and time the comment was created.
        content (TextField): The content of the comment.
    """

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comments")
    creator = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="comments"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    content = models.TextField()

    def __str__(self) -> str:
        """
        Returns:
            str: The content of the comment.
        """
        return str(self.content)


class Mention(models.Model):
    """
    A class that represents a mention.

    Attributes:
        comment (ForeignKey): The comment the mention is associated with.
        mentioned_user (ForeignKey): The user who was mentioned.
        created_at (DateTimeField): The date and time the mention was created.
    """

    comment = models.ForeignKey(
        Comment, on_delete=models.CASCADE, related_name="mentions"
    )
    mentioned_user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="mentions"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        """
        Returns:
            str: The user who was mentioned.
        """
        return str(self.mentioned_user)
