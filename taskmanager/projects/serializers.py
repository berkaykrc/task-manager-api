"""
This module contains the serializer classes for the Project model.

The ProjectSerializer class is responsible for serializing and deserializing
Project instances into JSON representations.

Example usage:
    # Create a new project
    serializer = ProjectSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
"""

from rest_framework import serializers
from tasks.serializers import TaskSerializer

from .models import Project


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer class for the Project model.
    """
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        """
        Meta class for defining metadata options for the Project serializer.
        """

        model = Project
        fields = ["id", "name", "description",
                  "start_date", "end_date", "users", "owner", "tasks"]
