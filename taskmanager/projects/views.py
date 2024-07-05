"""
This module contains the viewset for managing projects.

The ProjectViewSet class is a viewset that provides CRUD operations for the Project model.

Attributes:
    queryset (QuerySet): The queryset of all projects.
    serializer_class (Serializer): The serializer class for the Project model.
"""
import logging

from rest_framework import viewsets
from rest_framework.response import Response

from .models import Project
from .permissions import IsProjectOwnerOrReadOnly
from .serializers import ProjectSerializer, SharedFileSerializer

logger = logging.getLogger('taskmanager.projects.views')


class ProjectViewSet(viewsets.ModelViewSet):
    """
    A viewset for managing projects.

    This viewset provides CRUD operations (Create, Retrieve, Update, Delete)
    for the Project model.

    Attributes:
        queryset (QuerySet): The queryset of all projects.
        serializer_class (Serializer): The serializer class for the Project model.
    """

    queryset = Project.objects.all().order_by('id')
    serializer_class = ProjectSerializer
    permission_classes = [IsProjectOwnerOrReadOnly]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        projects_with_files = []
        for project in queryset:
            project_data = ProjectSerializer(
                project, context={'request': request}).data
            project_data['files'] = SharedFileSerializer(
                project.sharedfile_set.all(), context={'request': request}, many=True).data
            projects_with_files.append(project_data)
        return Response(projects_with_files)

    def create(self, request, *args, **kwargs):
        logger.debug("Creating a new project with data: %s", request.data)
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        logger.debug("Retrieving project with ID: %s", kwargs.get('pk'))
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        logger.debug("Updating project with ID: %s", kwargs.get('pk'))
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        logger.debug("Deleting project with ID: %s", kwargs.get('pk'))
        return super().destroy(request, *args, **kwargs)

    def get_serializer_context(self):
        return {'request': self.request}
