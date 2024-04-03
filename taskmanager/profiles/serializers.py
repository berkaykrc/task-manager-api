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

    image_url = serializers.SerializerMethodField()

    class Meta:
        """
        Meta class for defining metadata options for the Profile serializer.
        """

        model = Profile
        fields = ["user", "image_url"]

    def get_image_url(self, obj):
        """Return profile's image."""
        return obj.image.url if obj.image else None


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.

    This serializer is used to serialize/deserialize User objects.
    It includes fields for username, email, and image.
    """
    tasks = serializers.HyperlinkedRelatedField(
        many=True, read_only=True, view_name="task-detail"
    )
    image = serializers.SerializerMethodField()

    class Meta:
        """
        Meta class for defining metadata options for the serializer.
        """

        model = get_user_model()
        fields = ["username", "email", "image", "tasks"]

    def get_image(self, obj):
        """
        Return the URL of the user's image.

        If the user has a profile and an image is associated with the profile,
        the URL of the image is returned. Otherwise, None is returned.
        """
        return obj.profile.image.url if obj.profile and obj.profile.image else None


class UserRegistrationSerializer(serializers.ModelSerializer):
    """User registration serializer.

    Serializes the user registration data and validates it.

    Attributes:
        model (Model): The user model to be used for registration.
        fields (list): The fields to be included in the serialized data.

    """

    class Meta:
        """
        Meta class for defining metadata options for the serializer.
        """

        model = get_user_model()
        fields = ["username", "email", "password"]
