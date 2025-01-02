"""Profiles views."""

from dj_rest_auth.views import LoginView as DjRestAuthLoginView
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from profiles.permissions import IsAdminUserOrReadOnly, IsUserOrReadOnly
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

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

    queryset = Profile.objects.all().order_by("id")
    serializer_class = ProfileSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsUserOrReadOnly, IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        """
        Destroy a profile.

        Args:
            request: HTTP request.
            *args: Additional arguments.
            **kwargs: Additional keyword arguments.
        Returns:
            Response: The http response indicating the result of the operation.
        """
        instance = self.get_object()
        profile_id = instance.id
        user_id = instance.user.id
        self.perform_destroy(instance)
        return Response(
            {
                "message": "Profile deleted successfully.",
                "profile_id": profile_id,
                "user_id": user_id,
            },
            status=status.HTTP_204_NO_CONTENT,
        )

    def perform_destroy(self, instance):
        """
        Perform the destroy operation.

        Args:
            instance: The profile instance to be deleted.
        """
        instance.delete()

    @action(detail=True, methods=["patch"])
    def set_expo_push_token(self, request):
        """
        Set the Expo push token for a profile.

        Args:
            request: HTTP request.
            pk: The profile ID.

        Returns:
            Response object.
        """
        profile = self.get_object()
        expo_push_token = request.data.get("expo_push_token")

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

    queryset = get_user_model().objects.all().order_by("id")
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUserOrReadOnly, IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.

    Inherits from `viewsets.ModelViewSet` and provides CRUD actions for groups.
    """

    queryset = Group.objects.all().order_by("id")
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
    """
    A view for handling user login.

    This view extends the `DjRestAuthLoginView` class and adds additional functionality throttling
    the login requests using the `AnonRateThrottle` and `UserRateThrottle` classes.

    Throttling helps to prevent abuse and protect the server from excessive login attempts.

    Attributes:
        throttle_classes (list): A list of throttle classes to apply to the view.
    """

    throttle_classes = [AnonRateThrottle, UserRateThrottle]
