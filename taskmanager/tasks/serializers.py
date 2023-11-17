# create tasks seraializer.py
from rest_framework import serializers
from .models import Task
from profiles.serializers import ProfileSerializer


class TaskSerializer(serializers.HyperlinkedModelSerializer):
    assigned = ProfileSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = ['name', 'description', 'assigned', 'start_date', 'end_date', 'priority', 'status']





