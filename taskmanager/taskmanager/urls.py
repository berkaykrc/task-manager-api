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
from dj_rest_auth.views import PasswordResetConfirmView, PasswordResetView
from django.contrib import admin
from django.urls import include, path
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView
from profiles.views import LoginView, RegisterView

from .views import APIRootView

urlpatterns = [
    path("", APIRootView.as_view(), name="api-root"),
    path("admin/", admin.site.urls),
    path("login/", LoginView.as_view(), name="login"),
    path("register/", RegisterView.as_view(), name="register"),
    path("tasks/", include("tasks.urls")),
    path("profiles/", include("profiles.urls")),
    path("projects/", include("projects.urls")),
    path('password/reset/',
         PasswordResetView.as_view(), name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path("api-auth/", include("dj_rest_auth.urls")),
    path("graphql/", csrf_exempt(GraphQLView.as_view(graphiql=True))),
    path("__debug__/", include(debug_toolbar.urls)),
]
