"""
This module defines the URL patterns for the tasks app.

It includes a router that automatically generates the URL patterns for the TaskViewSet.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CommentViewSet, MentionViewSet, TaskViewSet

router = DefaultRouter()
router.register(r"comments", CommentViewSet)
router.register(r"mentions", MentionViewSet)
router.register(r"", TaskViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
