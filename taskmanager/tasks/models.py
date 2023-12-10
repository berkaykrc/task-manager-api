from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_start_date(value):
    if value < timezone.now():
        raise ValidationError('Start date cannot be in the past')


def validate_end_date(value):
    if value < timezone.now():
        raise ValidationError('End date cannot be in the past')

class Task(models.Model):
    name = models.CharField(max_length=255)
    start_date = models.DateTimeField(validators=[validate_start_date, validate_dates])
    end_date = models.DateTimeField(validators=[validate_end_date, validate_dates])
    description = models.TextField()
    PRIORITY_CHOICES = [
        ('ASAP', 'Asap'),
        ('MEDIUM', 'Medium'),
        ('LOW', 'Low'),
    ]
    priority = models.CharField(
        max_length=6, choices=PRIORITY_CHOICES, default='LOW')
    STATUS_CHOICES = [
        ('TODO', 'To Do'),
        ('INPROGRESS', 'In Progress'),
        ('DONE', 'Done'),
    ]
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='TODO')
    assigned = models.ManyToManyField(User, related_name='tasks')
    creator = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='created_tasks')

    @property
    @admin.display(
        boolean=True,
        ordering='start_date',
        description='Is the task overdue?',
    )
    def duration(self):
        if self.start_date and self.end_date:
            duration = self.end_date - self.start_date
            if duration.total_seconds() < 0:
                return 'Error: End date is earlier than start date'
            else:
                total_seconds = int(duration.total_seconds())
                hours, remainder = divmod(total_seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                return f'{hours}h {minutes}m'
        else:
            return "Error: start_date and/or end_date is not set"

    def __str__(self):
        return self.name
