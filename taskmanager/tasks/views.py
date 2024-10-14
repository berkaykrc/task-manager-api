"""
This module contains the viewset for managing tasks in the Task Manager API.

The TaskViewSet class provides CRUD operations for tasks, along with additional actions
such as assigning a task to a user.
"""
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import decorators, filters, response, status, viewsets
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Comment, Mention, Project, Task
from .permissions import (
    IsCreatorOrReadOnly,
    IsMentionedUser,
    IsProjectMember,
    IsProjectMemberOrReadOnly,
)
from .serializers import (
    CommentReadSerializer,
    CommentSerializer,
    CommentUpdateSerializer,
    MentionSerializer,
    TaskSerializer,
)


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
    permission_classes = [IsCreatorOrReadOnly, IsProjectMemberOrReadOnly]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["priority", "status", "shared_files"]
    search_fields = ["name", "description", "priority", "status"]
    ordering_fields = ["priority", "status",
                       "end_date", "duration", "created_at"]
    ordering = [
        "priority",
    ]

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
            return response.Response({"error": "Invalid duration"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(instance)
        return response.Response(serializer.data)

    @decorators.action(detail=True, methods=["post"])
    def assign_task(self, request, pk=None):
        """
        Assigns a task to a user.

        Args:
            request (HttpRequest): The request object.
            user_id (int): The ID of the user to assign the task to.

        Returns:
            HttpResponse: The response indicating the task has been assigned.
        """
        task = self.get_object()
        user_id = request.data.get("user_id")
        try:
            user = get_user_model().objects.get(pk=user_id)
        except get_user_model().DoesNotExist:
            return response.Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        if request.user not in task.project.users.all() and request.user != task.project.owner:
            return response.Response({"error": "User is not a member of the project or owner"},
                                     status=status.HTTP_403_FORBIDDEN)
        task.assigned.add(user)
        task.save()
        return response.Response({
            "response": f"Task assigned to {user.get_username()}"}, status=200)

    @decorators.action(detail=True, methods=["post", "put"])
    def remove_user_from_task(self, request, pk=None):
        """
        Removes a user from a task.

        Args:
            request (HttpRequest): The request object.

        Returns:
            HttpResponse: Theresponse indicating the user has been removed from the task or an error occured.
        """

        task = self.get_object()
        user_id = request.data.get("user_id")

        if not user_id:
            return response.Response({"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = get_user_model().objects.get(pk=user_id)
        except get_user_model().DoesNotExist:
            return response.Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return response.Response({"error": "Invalid user ID"}, status=status.HTTP_400_BAD_REQUEST)
        if user not in task.assigned.all():
            return response.Response({"error": "User is not assigned to the task"}, status=status.HTTP_404_NOT_FOUND)

        task.assigned.remove(user)
        task.save()
        return response.Response({
            "response": f"User {user.get_username()} removed from the task"}, status=status.HTTP_200_OK)

    @ decorators.action(detail=True, methods=["patch"], url_path=r"comments/(?P<comment_id>\\d+)")
    def update_comment(self, request, _pk=None, comment_id=None):
        """
        Updates a comment for a task.

        Args:
            request (HttpRequest): The request object.
            pk (int): The ID of the task.
            comment_id (int): The ID of the comment to update.

        Returns:
            HttpResponse: The response containing the updated comment data or an error message.
        """
        task = self.get_object()
        try:
            comment = task.comments.get(id=comment_id)
        except Comment.DoesNotExist:
            return response.Response({"error": "Comment not found"}, status=404)
        serializer = CommentUpdateSerializer(
            comment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return response.Response(serializer.data)
        return response.Response(serializer.errors, status=400)

    def perform_create(self, serializer):
        """
        Performs additional actions when creating a task.

        Sets the creator of the task to the current user.

        Args:
            serializer (Serializer): The serializer instance.

        Returns:
            None
        """
        project_url = self.request.data.get("project")
        # Extract the project ID from the URL string
        project_id = project_url.rstrip('/').split('/')[-1]
        project = Project.objects.get(pk=project_id)
        if self.request.user not in {project.owner, *project.users.all()}:
            raise ValidationError("You are not a member of this project")
        serializer.save(creator=self.request.user)


class MentionViewSet(viewsets.ModelViewSet):
    """
    A viewset for managing mentions.

    This viewset provides CRUD operations for mentions.

    Attributes:
        queryset (QuerySet): The queryset of mentions.
        serializer_class (Serializer): The serializer class for mentions.
        authentication_classes (list): The authentication classes for the viewset.
        permission_classes (list): The permission classes for the viewset.
    """

    queryset = Mention.objects.all()
    serializer_class = MentionSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsMentionedUser]


class CommentViewSet(viewsets.ModelViewSet):
    """
    A viewset for managing comments.

    This viewset provides CRUD operations for comments.

    Attributes:
        queryset (QuerySet): The queryset of comments.
        serializer_class (Serializer): The serializer class for comments.
        authentication_classes (list): The authentication classes for the viewset.
        permission_classes (list): The permission classes for the viewset.
    """

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsCreatorOrReadOnly, IsProjectMember]

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    def get_serializer_class(self):
        """
        Return the serializer class for the view.
        """
        if self.action in ("list", "retrive"):
            return CommentReadSerializer
        return CommentSerializer
