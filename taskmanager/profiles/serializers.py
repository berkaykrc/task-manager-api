"""Profiles serializers.

Serializers define the API representation.

Serializers convert model instances to JSON so that the frontend can work with the received data.

Attributes:

    ProfileSerializer: Profile serializer.
    UserSerializer: User serializer.
    UserRegistrationSerializer: User registration serializer.
"""
from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Profile


class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    """Profile serializer."""

    tasks = serializers.HyperlinkedRelatedField(
        many=True, read_only=True, view_name="task-detail"
    )
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ["user", "image_url", "tasks"]

    def get_image_url(self, obj):
        """Return profile's image."""
        return obj.image.url if obj.image else None


class UserSerializer(serializers.ModelSerializer):
    """User serializer."""

    image = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = ["username", "email", "image"]

    def get_image(self, obj):
        """Return user's image."""
        return obj.profile.image.url if obj.profile and obj.profile.image else None


class UserRegistrationSerializer(serializers.ModelSerializer):
    """User registration serializer."""

    class Meta:
        model = get_user_model()
        fields = ["username", "email", "password"]
