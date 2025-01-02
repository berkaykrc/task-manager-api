"""
URLs for the files app.

This module defines the URLs for the files app in the Task Manager API.
It includes a router for handling file-related endpoints and
registers the SharedFileViewSet as the viewset for the "files" endpoint.

Example usage:
    # Import the URLs in your project's main urls.py file
    path("files/", include("taskmanager.files.urls")),

"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import SharedFileViewSet

router = DefaultRouter()
router.register(r"", SharedFileViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
