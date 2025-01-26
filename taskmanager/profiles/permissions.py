"""
This module contains custom permissions for the task manager API.

The IsUserOrReadOnly permission class allows only the user of an object to edit it.
"""

from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView

from .models import Profile


class IsUserOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow users of an object to edit it.
    """

    def has_object_permission(
        self, request: Request, view: APIView, obj: Profile
    ) -> bool:
        """
        Check if the user has permission to perform the requested action on the object.

        Args:
            request (Request): The request object.
            view (APIView): The view object.
            obj (Profile): The object being accessed.

        Returns:
            bool: True if the user has permission, False otherwise.
        """
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the user of the object.
        return obj.user == request.user


class IsAdminUserOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admin users to edit objects.
    """

    def has_permission(self, request: Request, view: APIView) -> bool:
        """
        Check if the user has permission to perform the requested action on the view.

        Args:
            request (Request): The request object.
            view (APIView): The view object.

        Returns:
            bool: True if the user has permission, False otherwise.
        """
        if request.method in permissions.SAFE_METHODS:
            return True

        return bool(request.user and request.user.is_staff)
