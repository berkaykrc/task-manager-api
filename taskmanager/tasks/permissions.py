"""
This module contains custom permissions for the tasks app.

The permissions defined in this module are used to control access to task objects.
"""

from rest_framework import permissions


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

    def has_object_permission(self, request, _view, obj):
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


class IsProjectMemberOrReadyOnly(permissions.BasePermission):
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

    def has_object_permission(self, request, _view, obj):
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

        project = obj.project
        return project.owner == request.user or project.users.filter(pk=request.user.pk).exists()
