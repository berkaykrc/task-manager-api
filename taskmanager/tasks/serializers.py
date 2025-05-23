"""
This module contains the serializer classes for the Task model.

The serializers are used to convert Task model instances to JSON and vice versa.
They specify the fields to be included in the serialized representation of a Task object.

Classes:
    TaskSerializer: Serializer class for the Task model.
    CommentSerializer: Serializer class for the Comment model.
    MentionSerializer: Serializer class for the Mention model.
    CommentUpdateSerializer: Serializer class for updating a Comment instance.
    CommentReadSerializer: Serializer class for reading a Comment instance.
"""

import re
from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from .models import Comment, Mention, Project, Task


class MentionSerializer(serializers.ModelSerializer):
    """
    Serializer class for the Mention model.

    This serializer is used to convert Mention model instances to JSON
    and vice versa. It specifies the fields to be included in the
    serialized representation of a Mention object.
    """

    class Meta:
        """
        Meta class for defining metadata options for the MentionSerializer class.

        Attributes:
            model (class): The model
            fields (list): The list of fields to include in serialized representation of the model.
        """

        model = Mention
        fields = [
            "pk",
            "mentioned_user",
            "created_at",
        ]
        read_only_fields = ["created_at"]


class CommentUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer class for the Comment model.

    This serializer is used to convert Comment model instances to JSON
    and vice versa. It specifies the fields to be included in the
    serialized representation of a Comment object.
    """

    class Meta:
        """
        Meta class for defining metadata options for the CommentSerializer class.

        Attributes:
            model (class): The model
            fields (list): The list of fields to include in serialized representation of the model.
        """

        model = Comment
        fields = ["content"]


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer class for the Comment model.

    This serializer is used to convert Comment model instances to JSON
    and vice versa. It specifies the fields to be included in the
    serialized representation of a Comment object.

    Attributes:
        task: A nested TaskSerializer instance representing the task the comment belongs to.
    """

    task = "TaskSerializer"

    class Meta:
        """
        Meta class for defining metadata options for the CommentSerializer class.

        Attributes:
            model (class): The model class that the serializer is based on.
            fields (list): The list of fields to include in serialized representation of the model.
        """

        model = Comment
        fields = [
            "url",
            "pk",
            "task",
            "created_at",
            "creator",
            "content",
        ]
        read_only_fields = ["created_at", "creator"]

    def create(self, validated_data: dict[str, Any]) -> Comment:
        """
        Creates a new comment instance.

        This method overrides the default create method to add support for mentions in comments.
        It extracts mentions from the comment text and creates Mention instances for each mention.

        Args:
            validated_data (dict): The validated data for the new comment.

        Returns:
            Comment: The newly created comment instance.
        """
        comment = super().create(validated_data)
        text = comment.content
        mentions = re.findall(r"@(\w+)", text)
        for username in mentions:
            try:
                user = get_user_model().objects.get(username=username)
                Mention.objects.create(mentioned_user=user, comment=comment)
            except get_user_model().DoesNotExist:
                pass
        return comment

    def update(self, instance: Comment, validated_data: dict) -> Comment:
        """
        Updates an existing comment instance.

        This method overrides the default update method to add support for mentions in comments.
        It extracts mentions from the comment text and creates Mention instances for each mention.

        Args:
            instance (Comment): The existing comment instance to update.
            validated_data (dict): The validated data for the updated comment.

        Returns:
            Comment: The updated comment instance.
        """
        instance.content = validated_data.get("content", instance.content)
        instance.save()

        text = instance.content
        mentions = re.findall(r"@(\w+)", text)

        for username in mentions:
            try:
                user = get_user_model().objects.get(username=username)
                Mention.objects.get_or_create(mentioned_user=user, comment=instance)
            except get_user_model().DoesNotExist:
                pass
        for mention in instance.mentions.all():
            if "@" + mention.mentioned_user.username not in mentions:
                mention.delete()
        return instance


class CommentReadSerializer(CommentSerializer):
    """
    Serializer class for the Comment model.

    This serializer is used to convert Comment model instances to JSON
    and vice versa. It specifies the fields to be included in the
    serialized representation of a Comment object.

    Attributes:
        mentions (MentionSerializer): Serializer for the mentions field.

    Inherits:
        CommentSerializer: Base serializer class for the Comment model.
    """

    class Meta(CommentSerializer.Meta):
        """
        Meta class for defining metadata options for the CommentReadSerializer class.

        Attributes:
            model (class): The model class to be serialized.
            fields (list): The list of fields to include in the serialized representation of the model.
        """

        fields = CommentSerializer.Meta.fields + ["mentions"]


class TaskSerializer(serializers.HyperlinkedModelSerializer[Task]):
    """
    Serializer class for the Task model.

    This serializer is used to convert Task model instances to JSON
    and vice versa. It specifies the fields to be included in the
    serialized representation of a Task object.

    Attributes:
        comments: A nested CommentSerializer instance representing the comments for the task.
        creator: A HyperlinkedRelatedField instance representing the creator of the task.
    Methods:
        validate: Custom validation method to ensure that the start_date is before the end_date.

    """

    comments = CommentSerializer(many=True, read_only=True)
    creator: serializers.RelatedField = serializers.HyperlinkedRelatedField(
        view_name="user-detail", read_only=True
    )

    class Meta:
        """
        Meta class for defining metadata options for the TaskSerializer class.

        Attributes:
            model (class): The model class that the serializer is based on.
            fields (list): The list of fields to include in serialized representation of the model.
        """

        model = Task
        fields = [
            "url",
            "pk",
            "creator",
            "name",
            "description",
            "assigned",
            "start_date",
            "end_date",
            "priority",
            "status",
            "duration",
            "project",
            "comments",
            "shared_files",
        ]

        read_only_fields = ["creator"]

    def update(self, instance: Task, validated_data: dict[str, Any]) -> Task:
        """
        Updates an existing task instance.

        This method overrides the default update method to add support for assigning users
        at the current list of users of the task.

        Args:
            instance (Task): The existing task instance to update.
            validated_data (dict): The validated data for the updated task.

        Returns:
            Task: The updated task instance.
        """
        if "assigned" in validated_data:
            existing_users = set(instance.assigned.all())
            new_users = set(validated_data["assigned"])
            updated_assigned_users = existing_users.union(new_users)
            instance.assigned.set(updated_assigned_users)
            validated_data.pop("assigned")
        return super().update(instance, validated_data)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """
        Custom validation method to ensure that the start_date is before the end_date.

        Args:
            attrs (dict): The data to be validated.

        Raises:
            serializers.ValidationError: If the end_date is before the start_date.

        Returns:
            dict: The validated data.

        """
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError("end_date must be after start_date")
        return attrs

    def validate_assigned(self, value: list[AbstractUser]) -> list[AbstractUser]:
        """
        Validates that all users in the list are members of the project.

        Args:
            value (list[User]): List of users assigned to the task.

        Returns:
            list[User]: The validated list of users.

        Raises:
            serializers.ValidationError: If any user is not a member of the project.
        """
        request = self.context.get("request", None)
        project_url = request.data.get("project", None) if request else None
        project = None

        if project_url:
            project_id = project_url.rstrip("/").split("/")[-1]
            project = get_object_or_404(Project, pk=project_id)
        elif self.instance and hasattr(self.instance, "project"):
            project = self.instance.project

        if not project:
            raise serializers.ValidationError(
                "The task must be associated with a project."
            )

        for user in value:
            if user not in project.users.all():
                raise serializers.ValidationError("User is not a member of the project")

        return value
