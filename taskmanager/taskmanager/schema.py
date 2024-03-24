"""
This module defines the root query for the GraphQL API.

It contains the `Query` class, which serves as the entry point for all GraphQL queries.
The `Query` class inherits from the `tasks.schema.Query` and `profiles.schema.Query` classes,
and is based on the `graphene.ObjectType` class.

Attributes:
    schema (graphene.Schema): The GraphQL schema object.

Example:
    The following code demonstrates how to use the `Query` class:

    ```python
    schema = graphene.Schema(query=Query)
    ```
"""

import graphene
import graphql_jwt
import profiles.schema
import tasks.schema


class Query(tasks.schema.Query, profiles.schema.Query, graphene.ObjectType):
    """
    The root query for the GraphQL API.

    This class inherits from the `Query` class defined in the
    `tasks.schema` and `profiles.schema`module.
    It serves as the entry point for all GraphQL queries.

    Args:
        tasks.schema.Query: The query class for tasks.
        profiles.schema.Query: The query class for profiles.
        graphene.ObjectType: The base class for GraphQL object types.
    """


class Mutation(tasks.schema.Mutation, graphene.ObjectType):
    """
    The root mutation for the GraphQL API.

    This class inherits from the `Mutation` class defined in the
    `tasks.schema` module.
    It serves as the entry point for all GraphQL mutations.

    Args:
        tasks.schema.Mutation: The mutation class for tasks.
        graphene.ObjectType: The base class for GraphQL object types.

    Attributes:
        token_auth (graphql_jwt.ObtainJSONWebToken.Field): Mutation field for obtaining JWT.
        verify_token (graphql_jwt.Verify.Field): Mutation field for verifying JSON Web Token.
        refresh_token (graphql_jwt.Refresh.Field): Mutation field for refreshing JSON Web Token.
    """

    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
