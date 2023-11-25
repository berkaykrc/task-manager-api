# create tasks seraializer.py
from rest_framework import serializers
from .models import Task
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['username', 'email', 'image']

    def get_image(self, obj):
        return obj.profile.image.url if obj.profile and obj.profile.image else None


class TaskSerializer(serializers.HyperlinkedModelSerializer):
    assigned = UserSerializer(many=True, read_only=True)
    creator = UserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'creator', 'name', 'description', 'assigned',
                  'start_date', 'end_date', 'priority', 'status', 'duration']
