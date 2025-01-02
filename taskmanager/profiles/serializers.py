"""Profiles serializers.

Serializers define the API representation.

Serializers convert model instances to JSON so that the frontend can work with the received data.

Attributes:
    ProfileSerializer: Profile serializer.
    UserSerializer: User serializer.
    UserRegistrationSerializer: User registration serializer.
    GroupSerializer: Group serializer.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from rest_framework import serializers

from .models import Profile


class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for the Profile model.

    This serializer is used to convert Profile model instances to JSON
    representation and vice versa. It defines the fields that should be
    included in the serialized output and provides methods for custom
    serialization.

    Attributes:
        image (serializers.SerializerMethodField): A serializer field
            that represents the URL of the profile's image.

    Meta:
        model (Profile): The model class associated with this serializer.
        fields (list): The list of fields to be included in the serialized
            output.
    """

    image = serializers.ImageField(max_length=None, allow_empty_file=True, use_url=True)

    class Meta:
        model = Profile
        fields = ["user", "image", "expo_push_token"]


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for the Group model.

    This serializer is used to serialize/deserialize Group objects.
    It includes fields for name and permissions.

    Attributes:
        permissions(serializers.SlugRelatedField): A field that represents the related permissions for the group.
    """

    permissions = serializers.SlugRelatedField(
        many=True, queryset=Permission.objects.all(), slug_field="codename"
    )

    class Meta:
        model = Group
        fields = ["name", "permissions"]


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.

    This serializer is used to serialize/deserialize User objects.
    It includes fields for username, email, and image.

    Attributes:
        tasks(serializers.HyperlinkedRelatedField): A field that represents the related tasks for the user.
        image(serializers.SerializerMethodField): A method field that returns the URL of the user's image.
        groups(GroupSerializer): A serializer for the related groups of the user.

    Meta:
        model(User): The User model that the serializer is based on.
        fields(list): The fields to include in the serialized representation of the User model.

    Methods:
        create(validated_data): Create a new User instance with the provided validated data.
        update(instance, validated_data): Update an existing User instance with the provided validated data.
        get_image(obj): Return the URL of the user's image.
    """

    tasks = serializers.HyperlinkedRelatedField(
        many=True, read_only=True, view_name="task-detail"
    )
    image = serializers.SerializerMethodField()
    groups = GroupSerializer(many=True)
    projects = serializers.HyperlinkedRelatedField(
        many=True, view_name="project-detail", read_only=True
    )

    class Meta:
        model = get_user_model()
        fields = ["username", "email", "image", "tasks", "groups", "projects"]

    def create(self, validated_data):
        groups_data = validated_data.pop("groups")
        user = get_user_model().objects.create(**validated_data)
        for group_data in groups_data:
            group, _ = Group.objects.get_or_create(**group_data)
            user.groups.add(group)
        return user

    def update(self, instance, validated_data):
        groups_data = validated_data.pop("groups")
        instance.groups.clear()
        for group_data in groups_data:
            group, _ = Group.objects.get_or_create(**group_data)
            instance.groups.add(group)
        return super().update(instance, validated_data)

    def get_image(self, obj):
        """
        Return the URL of the user's image.

        Args:
            obj(User): The user object to get the image URL for.

        Returns:
            str: The URL of the user's image.

        """
        return obj.profile.image.url if obj.profile and obj.profile.image else None


class UserRegistrationSerializer(serializers.ModelSerializer):
    """User registration serializer.

    Serializes the user registration data and validates it.

    Attributes:
        model(Model): The user model to be used for registration.
        fields(list): The fields to be included in the serialized data.

    """

    class Meta:
        model = get_user_model()
        fields = ["username", "email", "password"]
