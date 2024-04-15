"""
This module contains the serializer classes for the Task model.

The serializers are used to convert Task model instances to JSON and vice versa.
They specify the fields to be included in the serialized representation of a Task object.

Classes:
    TaskSerializer: Serializer class for the Task model.

"""

from django.contrib.auth import get_user_model
from profiles.serializers import UserSerializer
from rest_framework import serializers

from .models import Task


class TaskSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer class for the Task model.

    This serializer is used to convert Task model instances to JSON
    and vice versa. It specifies the fields to be included in the
    serialized representation of a Task object.

    Attributes:
        assigned: A nested UserSerializer instance representing the assigned users.
        creator: A nested UserSerializer instance representing the creator of the task.

    Methods:
        validate: Custom validation method to ensure that the start_date is before the end_date.

    """

    assigned = serializers.PrimaryKeyRelatedField(
        many=True, read_only=False, queryset=get_user_model().objects.all())
    creator = UserSerializer(read_only=True)

    class Meta:
        """
        Meta class for defining metadata options for the TaskSerializer class.

        Attributes:
            model (class): The model class that the serializer is based on.
            fields (list): The list of fields to include in serialized representation of the model.
        """

        model = Task
        fields = [
            "url",
            "id",
            "creator",
            "name",
            "description",
            "assigned",
            "start_date",
            "end_date",
            "priority",
            "status",
            "duration",
            "project"
        ]

    def validate(self, attrs):
        """
        Custom validation method to ensure that the start_date is before the end_date.

        Args:
            attrs (dict): The data to be validated.

        Raises:
            serializers.ValidationError: If the end_date is before the start_date.

        Returns:
            dict: The validated data.

        """
        if attrs["start_date"] > attrs["end_date"]:
            raise serializers.ValidationError(
                "end_date must be after start_date")
        return attrs
