# project/urls.py

from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenObtainPairView,
)
from .views import APIRootView

def trigger_error(request):
    division_by_zero = 1 / 0

urlpatterns = [
    path('', APIRootView.as_view(), name='api-root'),
    path('admin/', admin.site.urls),
    path('tasks/', include('tasks.urls')),
    path('profiles/', include('profiles.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('api-auth/', include('rest_framework.urls', namespace='api-auth')),
    path('sentry-debug/', trigger_error),
    
]