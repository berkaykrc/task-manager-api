"""Views for the taskmanager app.

This file has the views for the taskmanager app.

Attributes:
    APIRootView (APIView): The API root view.


Methods:
    get: Gets the API root.
"""

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView


class APIRootView(APIView):
    """API root view.

    This class implements the API root view.

    Attributes:
        None.

    Methods:
        get: Gets the API root.
    """

    def get(self, request: Request) -> Response:
        """Gets the API root.

        This method gets the API root.

        Args:
            request (Request): The request.

        Returns:
            Response: The response.
        """

        return Response(
            {
                "tasks": reverse("task-list", request=request),
                "profiles": reverse("profile-list", request=request),
                "projects": reverse("project-list", request=request),
                "files": reverse("sharedfile-list", request=request),
            }
        )
