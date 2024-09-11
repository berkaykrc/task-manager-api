"""
This module contains the serializer classes for the Project model.

The ProjectSerializer class is responsible for serializing and deserializing
Project instances into JSON representations.

"""
from rest_framework import serializers

from .models import Project


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer class for the Project model.

    This serializer is used to convert Project model instances into JSON
    representations and vice versa. It specifies the fields that should be
    included in the serialized output and provides validation for incoming
    data.

    Attributes:
        tasks (TaskSerializer): Serializer for the related Task model.
        users (UserSerializer): Serializer for the related User model.
        owner (UserSerializer): Serializer for the related owner User model.
        shared_files (SharedFileSerializer): Serializer for the related SharedFile model.

    Meta:
        model (Project): The model class that this serializer is associated with.
        fields (list): The fields that should be included in the serialized output.
    """

    users = serializers.HyperlinkedRelatedField(
        many=True, view_name="user-detail", read_only=True)
    owner = serializers.HyperlinkedRelatedField(
        view_name="user-detail", read_only=True)

    class Meta:
        """
        Meta class for defining metadata options for the Project serializer.
        """

        model = Project
        fields = ["url", "id", "name", "description",
                  "start_date", "end_date", "users", "owner", "tasks", "shared_files"]
