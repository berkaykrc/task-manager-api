"""Profiles URLs.

This file has the URLs for the Profiles app.


Attributes:
    urlpatterns (list): The URLs for the Profiles app.
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import GroupViewSet, ProfileViewSet, UserViewSet

router = DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"groups", GroupViewSet)
router.register(r"", ProfileViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
