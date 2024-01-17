"""taskmanager URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/

Examples:

Function views
    1. Add an import:  from profiles import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from profiles.views import ProfileViewSet
    2. Add a URL to urlpatterns:  
        path('profiles/', ProfileViewSet.as_view({'get': 'list'}), name='profiles-list')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('profiles/', include('profiles.urls'))
"""
import debug_toolbar
from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import APIRootView

urlpatterns = [
    path("", APIRootView.as_view(), name="api-root"),
    path("admin/", admin.site.urls),
    path("tasks/", include("tasks.urls")),
    path("profiles/", include("profiles.urls")),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh", TokenRefreshView.as_view(), name="token_refresh"),
    path("api-auth/", include("rest_framework.urls", namespace="api-auth")),
    path("__debug__/", include(debug_toolbar.urls)),
]
