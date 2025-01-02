"""
This module defines the GraphQL schema for the profiles app.
It includes the definition of the `ProfileType`, `UserType`, and `Query` classes.

The `ProfileType` class represents a user profile in the GraphQL schema.
It defines the fields and behavior of the profile type.

The `UserType` class represents a user in the GraphQL schema.
It inherits from `DjangoObjectType` and includes a `profile` field of type `ProfileType`.

The `Query` class defines the queries that can be made on the `UserType`.
It includes a `resolve_all_users` method that returns all users in the system.
"""

import graphene
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from graphene_django import DjangoObjectType

from .models import Profile


class ProfileType(DjangoObjectType):
    """
    A GraphQL ObjectType representing a user profile.

    This class defines the GraphQL representation of a user profile.
    It is used to define the fields and behavior of the profile type in the GraphQL schema.

    Attributes:
        - Meta: A class that defines metadata options for the `ProfileType` class,
        such as the associated Django model and any additional fields.

    """

    class Meta:
        """
        Metadata options for the `ProfileType` class.

        This class defines the metadata options for the `ProfileType` class,
        such as the associated Django model and any additional fields.

        Attributes:
            - model: The Django model associated with the `ProfileType` class.
            - fields: The fields to include in the `ProfileType` class.
        """

        model = Profile
        fields = ("user", "image", "expo_push_token")


class UserType(DjangoObjectType):
    """
    Class that defines the UserType.

    Args:
        DjangoObjectType: Inherits from DjangoObjectType.

    Returns:
        Meta: Meta class that defines the model and the fields that will be included in the schema.
    """

    profile = graphene.Field(ProfileType)

    class Meta:
        """
        Meta class that defines the model and the fields that will be included in the schema.

        Args:
            DjangoObjectType: Inherits from DjangoObjectType.

        Returns:
            Meta: Meta class that defines the model and the fields that will be included in schema.

        """

        model = get_user_model()
        fields = ("username", "email", "profile")

    def resolve_image(self, _):
        """
        Method that resolves the image field of the UserType.

        Args:
            self: The object itself.
            info: The information about the request.

        Returns:
            str: The URL of the image of the user's profile.
        """
        if hasattr(self, "profile") and self.profile.image:
            return self.profile.image.url
        return None


class Query(graphene.ObjectType):
    """
    Class that defines the query for the UserType.

    Args:
        graphene.ObjectType: Inherits from graphene.ObjectType.

    Returns:
        QuerySet: The assigned_tasks field of the UserType.

    """

    all_users = graphene.List(UserType)

    def resolve_all_users(self, info):
        """
        Method that resolves the all_users field of the UserType.

        Args:
            self: The object itself.
            info: The information about the request.

        Returns:
            QuerySet: The assigned_tasks field of the UserType.
        """
        user = info.context.user
        if user.is_authenticated:
            return get_user_model().objects.all()
        raise PermissionDenied("Authentication credentials were not provided.")
