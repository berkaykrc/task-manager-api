# create tasks seraializer.py
from rest_framework import serializers
from .models import Task
from profiles.serializers import UserSerializer



class TaskSerializer(serializers.HyperlinkedModelSerializer):
    assigned = UserSerializer(many=True, read_only=True)
    creator = UserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'creator', 'name', 'description', 'assigned',
                  'start_date', 'end_date', 'priority', 'status', 'duration']
