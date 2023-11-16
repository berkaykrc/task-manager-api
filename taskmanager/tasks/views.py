from .serializers import TaskSerializer
from .models import Task
from rest_framework import viewsets, decorators, response, reverse
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

# Create your views here.

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    authentication_classes = [JWTAuthentication]

    @method_decorator(cache_page(60*60*2))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    @decorators.action(detail=True, methods=['post'])
    def assign_task(self, request, pk=None):
        task = self.get_object()
        user = request.user
        task.assigned.add(user)
        task.save()
        return response.Response({'status': 'task assigned'})

@decorators.api_view(['GET'])
def api_root(request, format=None):
    return response.Response({
        'users': reverse.reverse('user-list', request=request, format=format),
        'tasks': reverse.reverse('task-list', request=request, format=format),
        'profiles': reverse.reverse('profile-list', request=request, format=format),
    })

