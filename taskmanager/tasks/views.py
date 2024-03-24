"""
This module contains the viewset for managing tasks in the Task Manager API.

The TaskViewSet class provides CRUD operations for tasks, along with additional actions
such as assigning a task to a user.

Attributes:
    queryset (QuerySet): The queryset of tasks.
    serializer_class (Serializer): The serializer class for tasks.
    authentication_classes (list): The authentication classes for the viewset.
    permission_classes (list): The permission classes for the viewset.
    filter_backends (list): The filter backends for the viewset.
    filterset_fields (list): The fields to filter tasks by.
    search_fields (list): The fields to search tasks by.
    ordering_fields (list): The fields to order tasks by.
    ordering (list): The default ordering for tasks.
"""

from django.core.exceptions import ValidationError
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import decorators, filters, response, viewsets
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Task
from .permissions import IsCreatorOrReadOnly
from .serializers import TaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
    """
    A viewset for managing tasks.

    This viewset provides CRUD operations for tasks, along with additional actions
    such as assigning a task to a user.

    Attributes:
        queryset (QuerySet): The queryset of tasks.
        serializer_class (Serializer): The serializer class for tasks.
        authentication_classes (list): The authentication classes for the viewset.
        permission_classes (list): The permission classes for the viewset.
        filter_backends (list): The filter backends for the viewset.
        filterset_fields (list): The fields to filter tasks by.
        search_fields (list): The fields to search tasks by.
        ordering_fields (list): The fields to order tasks by.
        ordering (list): The default ordering for tasks.
    """

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsCreatorOrReadOnly]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["priority", "status"]
    search_fields = ["name", "description", "priority", "status"]
    ordering_fields = ["priority", "status"]
    ordering = [
        "priority",
    ]

    @method_decorator(cache_page(60))
    def dispatch(self, *args, **kwargs):
        """
        Dispatches the request to the appropriate handler method.

        This method is decorated with cache_page to cache the response for 60 seconds.

        Returns:
            HttpResponse: The response from the handler method.
        """
        return super().dispatch(*args, **kwargs)

    def retrieve(self, request, *_args, **_kwargs):
        """
        Retrieves a single task.

        If the task's duration is invalid, returns a 400 Bad Request response.

        Args:
            request (HttpRequest): The request object.
            *_args: Variable length argument list.
            **_kwargs: Arbitrary keyword arguments.

        Returns:
            HttpResponse: The response containing the serialized task data or an error message.
        """
        instance = self.get_object()
        try:
            instance.duration
        except ValidationError:
            return response.Response({"error": "Invalid duration"}, status=400)
        serializer = self.get_serializer(instance)
        return response.Response(serializer.data)

    @decorators.action(detail=True, methods=["post"])
    def assign_task(self, request, pk=None):
        """
        Assigns a task to a user.

        Args:
            request (HttpRequest): The request object.
            pk (int): The primary key of the task.

        Returns:
            HttpResponse: The response indicating the task has been assigned.
        """
        task = Task.objects.get(pk=pk)
        user = request.user
        task.assigned.add(user)
        task.save()
        return response.Response({"status": "task assigned"})

    def perform_create(self, serializer):
        """
        Performs additional actions when creating a task.

        Sets the creator of the task to the current user.

        Args:
            serializer (Serializer): The serializer instance.

        Returns:
            None
        """
        serializer.save(creator=self.request.user)
