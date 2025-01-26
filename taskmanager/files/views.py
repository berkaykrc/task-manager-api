"""
This module contains the views for handling shared files.

The views in this module are used for viewing and editing SharedFile instances.

Classes:
    SharedFileViewSet -- A viewset for viewing and editing SharedFile instances.
"""

from django.urls import resolve
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError

from .models import Project, SharedFile, Task
from .serializers import SharedFileSerializer


class SharedFileViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing SharedFile instances.
    """

    serializer_class = SharedFileSerializer
    queryset = (
        SharedFile.objects.all()
        .prefetch_related("project", "task", "uploaded_by")
        .order_by("pk")
    )

    def perform_create(self, serializer) -> None:
        """
        Perform create method for SharedFileViewSet.

        This method is called when a new SharedFile instance is created.
        It sets the owner of the SharedFile to the current user and ensures that the project and task are valid.

        """
        project = self.get_project()
        task = self.get_task()

        if task and task.project != project:
            raise ValidationError("The task does not belong to the project")
        try:
            serializer.save(uploaded_by=self.request.user, project=project, task=task)
        except Exception as exc:
            raise ValidationError("An error occurred while creating the file.") from exc

    def get_project(self) -> Project | None:
        """
        Get the project associated with the file.

        Returns:
            Project | None : The project associated with the file.
        """
        project_url = self.request.data.get("project")
        if project_url:
            project_id = resolve(project_url).kwargs.get("pk")
            if not project_id:
                raise ValidationError("Inalid project URL")
            try:
                project = Project.objects.get(pk=project_id)
            except Project.DoesNotExist as exc:
                raise ValidationError(
                    "There is no Project with this ID to relate to the file"
                ) from exc
            return project
        return None

    def get_task(self) -> Task | None:
        """
        Get the task associated with the file.

        Returns:
            Task: The task associated with the file.
        """
        task_url = self.request.data.get("task")
        if task_url:
            task_id = resolve(task_url).kwargs.get("pk")
            if not task_id:
                raise ValidationError("Invalid task URL")
            try:
                task = Task.objects.get(pk=task_id)
            except Task.DoesNotExist as exc:
                raise ValidationError(
                    "There is no Task with this ID to relate to project"
                ) from exc
            return task
        return None
