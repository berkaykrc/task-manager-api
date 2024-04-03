"""Profiles views."""

from dj_rest_auth.views import LoginView as DjRestAuthLoginView
from django.contrib.auth import get_user_model
from profiles.permissions import IsUserOrReadOnly
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Profile
from .serializers import ProfileSerializer, UserRegistrationSerializer, UserSerializer


class ProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to view or edit profiles.

    Inherits from `viewsets.ModelViewSet` and provides CRUD actions for profiles.
    Requires authentication and permission to access.
    """

    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsUserOrReadOnly]


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to view.

    Inherits from `viewsets.ReadOnlyModelViewSet` and provides read-only actions for users.
    """

    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer


class RegisterView(APIView):
    """
    API endpoint that allows users to be registered.

    Provides a POST method to register a user.
    Requires username, email, and password in the request data.
    Returns a response with the created user's refresh and access tokens if successful.
    """

    def post(self, request):
        """
        Register a user.

        Args:
            request: HTTP request.

        Returns:
            Response object.
        """

        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = get_user_model().objects.create_user(
                serializer.data["username"],
                serializer.data["email"],
                serializer.data["password"],
            )
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(DjRestAuthLoginView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
