"""Profiles views."""

from typing import Any

from dj_rest_auth.views import LoginView as DjRestAuthLoginView  # type: ignore
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication  # type: ignore
from rest_framework_simplejwt.tokens import RefreshToken

from profiles.permissions import IsAdminUserOrReadOnly, IsUserOrReadOnly

from .models import Profile
from .serializers import (
    GroupSerializer,
    ProfileSerializer,
    UserRegistrationSerializer,
    UserSerializer,
)


class ProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to view or edit profiles.

    Inherits from `viewsets.ModelViewSet` and provides CRUD actions for profiles.
    Requires authentication and permission to access.
    """

    queryset = Profile.objects.all().order_by("pk")
    serializer_class = ProfileSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsUserOrReadOnly, IsAuthenticated]

    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Destroy a profile.

        Args:
            request: HTTPRequest.
        Returns:
            Response: The HttpResponse indicating the result of the operation.
        """
        instance: Profile = self.get_object()
        profile_id = instance.pk
        user_id = instance.user.pk
        self.perform_destroy(instance)
        return Response(
            {
                "message": "Profile deleted successfully.",
                "profile_id": profile_id,
                "user_id": user_id,
            },
            status=status.HTTP_204_NO_CONTENT,
        )

    def perform_destroy(self, instance: Profile) -> None:
        """
        Perform the destroy operation.

        Args:
            instance: The Profile instance to be deleted.
        """
        instance.delete()

    @action(detail=True, methods=["patch"])
    def set_expo_push_token(self, request: Request, pk: int | None = None) -> Response:
        """
        Set the Expo push token for a profile.

        Args:
            request: HTTP request.
        Returns:
            Response object.
        """
        profile: Profile = self.get_object()
        expo_push_token: str | None = request.data.get("expo_push_token")

        if not expo_push_token:
            return Response(
                {"error": "Expo push token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        profile.expo_push_token = expo_push_token
        profile.save()

        return Response(
            {"message": "Expo push token set successfully."}, status=status.HTTP_200_OK
        )


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to view.

    Inherits from `viewsets.ReadOnlyModelViewSet` and provides read-only actions for users.
    """

    queryset = get_user_model().objects.all().order_by("pk")
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUserOrReadOnly, IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.

    Inherits from `viewsets.ModelViewSet` and provides CRUD actions for groups.
    """

    queryset = Group.objects.all().order_by("pk")
    serializer_class = GroupSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]


class RegisterView(APIView):
    """
    API endpoint that allows users to be registered.

    Provides a POST method to register a user.
    Requires username, email, and password in the request data.
    Returns a response with the created user's refresh and access tokens if successful.
    """

    def post(self, request: Request) -> Response:
        """
        Register a user.

        Args:
            request: HTTPRequest.

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
    """
    A view for handling user login.

    This view extends the `DjRestAuthLoginView` class and adds additional functionality throttling
    the login requests using the `AnonRateThrottle` and `UserRateThrottle` classes.

    Throttling helps to prevent abuse and protect the server from excessive login attempts.

    Attributes:
        throttle_classes (list): A list of throttle classes to apply to the view.
    """

    throttle_classes = [AnonRateThrottle, UserRateThrottle]
