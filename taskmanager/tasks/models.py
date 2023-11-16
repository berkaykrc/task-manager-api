from django.db import models
from django.contrib.auth.models import User


class Task(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
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
        return (self.end_date - self.start_date).total_seconds() / 60

    def __str__(self):
        return self.name
