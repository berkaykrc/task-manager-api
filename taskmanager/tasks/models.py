from django.db import models
from django.contrib.auth.models import User


class Task(models.Model):
    name = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
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

    @property
    def duration(self):
        if self.start_date and self.end_date:
            duration = self.end_date - self.start_date
            if duration.total_seconds() < 0:
                return 'Error: End date is earlier than start date'
            else:
                return duration.total_seconds() / 60
        else:
            return "Error: start_date and/or end_date is not set"

    def __str__(self):
        return self.name
