# project/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse

class APIRootView(APIView):
    def get(self, request, format=None):
        return Response({
            'tasks': reverse('task-list', request=request, format=format),
            'profiles': reverse('profile-list', request=request, format=format),
        })