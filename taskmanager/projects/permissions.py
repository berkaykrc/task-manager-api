"""
This module contains custom permissions for the projects app.

The IsOwnerOrReadOnly permission class allows only the owners of an object to edit it.
"""

from django.http import HttpRequest
from rest_framework import permissions
from rest_framework.views import APIView

from projects.models import Project


class IsProjectOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(
        self, request: HttpRequest, view: APIView, obj: Project
    ) -> bool:
        """
        Check if the user has permission to perform the requested action on the object.

        Args:
            request (HttpRequest): The request object.
            view (View): The view object.
            obj (Any): The object being accessed.

        Returns:
            bool: True if the user has permission, False otherwise.
        """
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the project.
        return request.user == obj.owner
