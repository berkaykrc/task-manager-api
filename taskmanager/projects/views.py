"""
This module contains the viewset for managing projects.

The ProjectViewSet class is a viewset that provides CRUD operations for the Project model.

Attributes:
    queryset (QuerySet): The queryset of all projects.
    serializer_class (Serializer): The serializer class for the Project model.
"""

from rest_framework import viewsets

from .models import Project
from .serializers import ProjectSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    """
    A viewset for managing projects.

    This viewset provides CRUD operations (Create, Retrieve, Update, Delete)
    for the Project model.

    Attributes:
        queryset (QuerySet): The queryset of all projects.
        serializer_class (Serializer): The serializer class for the Project model.
    """

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
