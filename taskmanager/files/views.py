"""
This module contains the views for handling shared files.

The views in this module are used for viewing and editing SharedFile instances.

Classes:
    SharedFileViewSet -- A viewset for viewing and editing SharedFile instances.
"""

from rest_framework import viewsets

from .models import SharedFile
from .serializers import SharedFileSerializer


class SharedFileViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing SharedFile instances.
    """
    serializer_class = SharedFileSerializer
    queryset = SharedFile.objects.all()
