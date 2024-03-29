"""Profiles URLs.

This file has the URLs for the Profiles app.


Attributes:
    urlpatterns (list): The URLs for the Profiles app.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import LoginView, ProfileViewSet, RegisterView, UserViewSet

router = DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"", ProfileViewSet)

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("register/", RegisterView.as_view(), name="register"),
    path("", include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
