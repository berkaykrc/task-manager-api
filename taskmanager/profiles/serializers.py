# serializers.py
from rest_framework import serializers
from .models import Profile
from django.contrib.auth.models import User


class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    tasks = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='task-detail'
    )
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['user', 'image_url', 'tasks']

    def get_image_url(self, obj):
        return obj.image.url if obj.image else None


class UserSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['username', 'email', 'image']

    def get_image(self, obj):
        return obj.profile.image.url if obj.profile and obj.profile.image else None
