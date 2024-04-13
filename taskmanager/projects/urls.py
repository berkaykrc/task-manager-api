"""
This module defines the URL patterns for the projects app.

It includes the URL patterns for the projects API endpoints using the Django REST Framework.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ProjectViewSet

router = DefaultRouter()
router.register(r"", ProjectViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
