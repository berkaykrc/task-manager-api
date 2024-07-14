"""
This module contains the serializer classes for the Task model.

The serializers are used to convert Task model instances to JSON and vice versa.
They specify the fields to be included in the serialized representation of a Task object.

Classes:
    TaskSerializer: Serializer class for the Task model.

"""

import re

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from profiles.serializers import UserSerializer
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
            "id",
            "mentioned_user",
            "created_at",
        ]


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
            "id",
            "task",
            "created_at",
            "creator",
            "content",
        ]

    def create(self, validated_data):
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
                pass  # If the user does not exist, we simply skip the mention
        return comment

    def update(self, instance, validated_data):
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
                Mention.objects.get_or_create(
                    mentioned_user=user, comment=instance)
            except get_user_model().DoesNotExist:
                pass
        for mention in instance.mentions.all():
            if '@' + mention.mentioned_user.username not in mentions:
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

    Example:
        To use this serializer, create an instance of CommentReadSerializer
        and pass a Comment object to it:

        >>> comment = Comment.objects.get(id=1)
        >>> serializer = CommentReadSerializer(comment)
        >>> serialized_data = serializer.data
    """
    class Meta(CommentSerializer.Meta):
        """
        Meta class for defining metadata options for the CommentReadSerializer class.

        Attributes:
            model (class): The model class to be serialized.
            fields (list): The list of fields to include in the serialized representation of the model.
        """
        fields = CommentSerializer.Meta.fields + ["mentions"]


class TaskSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer class for the Task model.

    This serializer is used to convert Task model instances to JSON
    and vice versa. It specifies the fields to be included in the
    serialized representation of a Task object.

    Attributes:
        assigned: A nested UserSerializer instance representing the assigned users.
        creator: A nested UserSerializer instance representing the creator of the task.

    Methods:
        validate: Custom validation method to ensure that the start_date is before the end_date.

    """

    assigned = serializers.PrimaryKeyRelatedField(
        many=True, queryset=get_user_model().objects.all())
    creator = UserSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

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
            "id",
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

    def update(self, instance, validated_data):
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

    def validate(self, attrs):
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
            raise serializers.ValidationError(
                "end_date must be after start_date")
        return attrs

    def validate_assigned(self, value):
        """
        Validates that all users in the list are members of the project.

        Args:
            value (list): List of users assigned to the task.

        Returns:
            list: The validated list of users.

        Raises:
            serializers.ValidationError: If any user is not a member of the project.
        """
        # Attempt to get the project from the request for new tasks
        project_url = self.context.get('request').data.get('project', None)
        project = None

        if project_url:
            project_id = project_url.rstrip('/').split('/')[-1]
            project = get_object_or_404(Project, id=project_id)
        elif self.instance and hasattr(self.instance, 'project'):
            project = self.instance.project

        if not project:
            raise serializers.ValidationError(
                "The task must be associated with a project.")

        for user in value:
            if user not in project.users.all():
                raise serializers.ValidationError(
                    "User is not a member of the project")

        return value
