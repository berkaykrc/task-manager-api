"""
This file contains the schema for the tasks app.

Classes:
    TaskType: A class that represents the task type.
    Query: A class that represents the query type.

Functions:
    resolve_all_tasks: A function that resolves all tasks.
    resolve_by_creator: A function that resolves tasks by creator.
"""

import graphene
from django.db.models import Q
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from profiles.schema import UserType

from .models import Task


class TaskType(DjangoObjectType):
    """
    A class that represents the task type.

    Methods:
        Meta: A class that contains the model and fields.

        Attributes:
            assigned: A list of users assigned to the task.
            creator: The user who created the task.
    """

    assigned = graphene.List(UserType)
    creator = graphene.Field(UserType)

    class Meta:
        """
        A class that contains the model and fields.

        Attributes:
            model: The model for the task.

            Methods:
                resolve_assigned: A method that resolves the users assigned to the task.
                resolve_creator: A method that resolves the user who created the task.
        """

        model = Task

    def resolve_assigned(self, _):
        """
        Resolve the assigned field.

        This method returns all the assigned users for a task.

        Args:
            _ (Any): Placeholder argument.

        Returns:
            QuerySet: A queryset containing all the assigned users for the task.
        """
        return self.assigned.all()

    def resolve_creator(self, _):
        """
        Resolves the user who created the task.

        Args:
            info: The query info.

        Returns:
            The user who created the task.
        """
        return self.creator


class Query(graphene.ObjectType):
    """
    A class that represents the query type.

    Methods:
        all_tasks: A method that resolves all tasks.
        task_by_creator: A method that resolves tasks by creator.
    """

    all_tasks = graphene.List(
        TaskType, search=graphene.String(), first=graphene.Int(), skip=graphene.Int()
    )
    task_by_creator = graphene.List(TaskType, creator=graphene.String())

    def resolve_all_tasks(self, _, search=None, first=None, skip=None):
        """
        Resolves all tasks.

        Args:
            _: The parent resolver info.
            search (str, optional): A string to search for in task names and descriptions.

        Returns:
            A list of all tasks that match the search criteria if provided, otherwise all tasks.

        """
        if search:
            filter_query = Q(name__icontains=search) | Q(description__icontains=search)
            return Task.objects.filter(filter_query)
        if first:
            return Task.objects.all()[:first]
        if skip:
            return Task.objects.all()[skip:]

        return Task.objects.all()

    def resolve_task_by_creator(self, _, creator):
        """
        Resolves tasks by creator.

        Args:
            info: The query info.
            creator: The creator of the task.

        Returns:
            A list of tasks by creator.
        """
        return Task.objects.filter(creator__username=creator)


class StatusEnum(graphene.Enum):
    """
    A class that represents the status enum.

    Attributes:


    """

    TODO = "To Do"
    INPROGRESS = "In Progress"
    DONE = "Done"


class CreateTask(graphene.Mutation):
    """
    A class that represents the create task mutation.

    Methods:
        Arguments: A class that represents the arguments for the mutation.
        Output: A class that represents the output for the mutation.
        mutate: A method that creates a task.
    """

    task = graphene.Field(TaskType)

    class Arguments:
        """
        A class that represents the arguments for the mutation.

        Attributes:
            name: The name of the task.
            description: The description of the task.
            creator: The creator of the task.
            assigned: The users assigned to the task.
            status: The status of the task.
        """

        name = graphene.String()
        description = graphene.String()
        status = StatusEnum()
        start_date = graphene.DateTime(required=True)
        end_date = graphene.DateTime(required=True)

    def mutate(
        self,
        info,
        name,
        status,
        description,
        start_date=None,
        end_date=None,
    ):
        """
        Creates a task.

        Args:
            info: The query info.
            name: The name of the task.
            description: The description of the task.
            status: The status of the task.
            start_date: The start date of the task.
            end_date: The end date of the task.

        Returns:
            The created task.
        """
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("You must be logged in to create a task!")

        task = Task.objects.create(
            name=name,
            description=description,
            creator=user,
            status=status.value,
            start_date=start_date,
            end_date=end_date,
        )

        return CreateTask(task=task)


class Mutation(graphene.ObjectType):
    """
    A class that represents the mutation type.

    Methods:
        create_task: A method that creates a task.
    """

    create_task = CreateTask.Field()
