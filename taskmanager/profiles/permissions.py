"""
This module contains custom permissions for the task manager API.

The IsUserOrReadOnly permission class allows only the user of an object to edit it.
"""

from rest_framework import permissions


class IsUserOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow users of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
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

        # Write permissions are only allowed to the user of the object.
        return obj.user == request.user
