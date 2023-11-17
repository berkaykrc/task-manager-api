from .serializers import TaskSerializer
from .models import Task
from rest_framework import viewsets, decorators, response
from rest_framework.reverse import reverse
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.exceptions import ValidationError

# Create your views here.


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    authentication_classes = [JWTAuthentication]

    @method_decorator(cache_page(60*60*2))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            duration = instance.duration
        except ValidationError as e:
            return response.Response({'error': str(e)}, status=400)
        serializer = self.get_serializer(instance)
        return response.Response(serializer.data)

    @decorators.action(detail=True, methods=['post'])
    def assign_task(self, request):
        task = self.get_object()
        user = request.user
        task.assigned.add(user)
        task.save()
        return response.Response({'status': 'task assigned'})
