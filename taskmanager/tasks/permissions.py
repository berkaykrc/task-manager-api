"""
This module contains custom permissions for the tasks app.

The permissions defined in this module are used to control access to task objects.

Classes:
    - IsCreatorOrReadOnly: Custom permission class that allows only the creators of a task to edit it.
    - IsProjectMemberOrReadOnly: Custom permission class that allows only project members to view and edit tasks associated with the project.
    - IsMentionedUser: Custom permission class that allows only the mentioned user to view and edit mentions associated with the user.
    - IsProjectMember: Custom permission class that allows only project members to view and edit comments associated with the project.
"""

from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView

from .models import Comment, Mention, Task


class IsCreatorOrReadOnly(permissions.BasePermission):
    """
    Custom permission class for Django REST Framework.

    This class extends `permissions.BasePermission` and overrides the `has_object_permission` method
    to allow only the creators of an object to edit it. If the request method is a safe method (GET, HEAD, OPTIONS),
    the permission is granted to any user. Otherwise, the permission is granted only to the user who is the creator of the object.

    Attributes:
        SAFE_METHODS: A tuple of HTTP methods considered safe for read-only operations.

    Methods:
        has_object_permission(request, view, obj): Determines if the user has permission to perform the requested action on the object.
    """

    def has_object_permission(self, request: Request, view: APIView, obj: Task) -> bool:
        """
        Check if the user has permission to perform the requested action on the task object.

        Args:
            request (HttpRequest): The request object.
            view (View): The view object.
            obj (Task): The task object.

        Returns:
            bool: True if the user has permission, False otherwise.
        """
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.creator == request.user


class IsProjectMemberOrReadOnly(permissions.BasePermission):
    """
    Custom permission class for Django REST Framework.

    This class extends `permissions.BasePermission` and overrides the `has_object_permission` method
    to allow only project members to view and edit tasks associated with the project. If the request method is a safe method (GET, HEAD, OPTIONS),
    the permission is granted to any user. Otherwise, the permission is granted only to users who are members of the project.

    Attributes:
        SAFE_METHODS: A tuple of HTTP methods considered safe for read-only operations.

    Methods:
        has_object_permission(request, view, obj): Determines if the user has permission to perform the requested action on the object.
    """

    def has_object_permission(self, request: Request, view: APIView, obj: Task) -> bool:
        """
        Check if the user has permission to perform the requested action on the task object.

        Args:
            request (Request): The request object.
            view (APIView): The view object.
            obj (Task): The task object.

        Returns:
            bool: True if the user has permission, False otherwise.
        """
        if request.method in permissions.SAFE_METHODS:
            return True

        return (
            obj.project.owner == request.user
            or obj.project.users.filter(pk=request.user.pk).exists()
        )


class IsMentionedUser(permissions.BasePermission):
    """
    Custom permission class for Django REST Framework.

    This class extends `permissions.BasePermission` and overrides the `has_object_permission` method
    to allow only the mentioned user to view and edit mentions associated with the user. If the request method is a safe method (GET, HEAD, OPTIONS),
    the permission is granted to any user. Otherwise, the permission is granted only to the mentioned user.

    Attributes:
        SAFE_METHODS: A tuple of HTTP methods considered safe for read-only operations.

    Methods:
        has_object_permission(request, view, obj): Determines if the user has permission to perform the requested action on the object.
    """

    def has_object_permission(
        self, request: Request, view: APIView, obj: Mention
    ) -> bool:
        """
        Check if the user has permission to perform the requested action on the mention object.

        Args:
            request (Request): The request object.
            view (APIView): The view object.
            obj (Mention): The mention object.

        Returns:
            bool: True if the user has permission, False otherwise.
        """
        if isinstance(obj, Mention):
            return obj.mentioned_user == request.user
        return False


class IsProjectMember(permissions.BasePermission):
    """
    Custom permission class for Django REST Framework.
    Determines if the user has permission to access a project-related object.
    """

    def has_object_permission(
        self, request: Request, view: APIView, obj: Comment
    ) -> bool:
        """
        Check if the user has permission to access the specified object.
        Args:
            request (Request): The request being made.
            view (APIView): The view handling the request.
            obj (Comment): The object being accessed.
        Returns:
            bool: True if the user has permission, False otherwise.
        """
        if request.method in permissions.SAFE_METHODS:
            return True

        task = obj.task
        project = task.project

        return (
            project.owner == request.user
            or project.users.filter(pk=request.user.pk).exists()
        )

    def has_permission(self, request: Request, view: APIView) -> bool:
        """
        Check if the user has permission to perform the specified action.

        Args:
            request (Request): The request being made.
            view (APIView): The view handling the request.

        Returns:
            bool: True if the user has permission, False otherwise.
        """
        if request.method == "POST":
            task_id = request.data.get("task")
            if task_id is not None:
                try:
                    task = Task.objects.get(pk=task_id)
                    return (
                        task.project.users.filter(pk=request.user.pk).exists()
                        or task.project.owner == request.user
                    )
                except Task.DoesNotExist:
                    return False
        return True
