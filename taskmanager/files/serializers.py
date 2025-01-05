"""
This module contains the serializers for the SharedFile model.
"""

from rest_framework import serializers

from .models import SharedFile


class SharedFileSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer class for the SharedFile model.

    This serializer is used to convert SharedFile model instances into JSON
    representations and vice versa. It specifies the fields that should be
    included in the serialized output.

    Attributes:
        file (FileField): The file associated with the shared file.
        uploaded_at (DateTimeField): The date and time when the file was uploaded.
        uploaded_by (ForeignKey): The user who uploaded the file.
        project (ForeignKey): The project associated with the shared file.
        task (ForeignKey): The task associated with the shared file.
    """

    uploaded_by: serializers.RelatedField = serializers.HyperlinkedRelatedField(
        view_name="user-detail", read_only=True
    )

    class Meta:
        model = SharedFile
        fields = ["url", "file", "uploaded_at", "uploaded_by", "project", "task"]
