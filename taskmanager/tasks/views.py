from .serializers import TaskSerializer
from .models import Task
from rest_framework import viewsets, decorators, response, filters, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.exceptions import ValidationError
from .permissions import IsCreatorOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsCreatorOrReadOnly]
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['priority', 'status']
    search_fields = ['name', 'description', 'priority', 'status']
    ordering_fields = ['priority', 'status']
    ordering = ['priority',]

    @method_decorator(cache_page(60*60*2))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            instance.duration
        except ValidationError as e:
            return response.Response({'error': str(e)}, status=400)
        serializer = self.get_serializer(instance)
        return response.Response(serializer.data)

    @decorators.action(detail=True, methods=['post'])
    def assign_task(self, request, pk=None):
        task = self.get_object()
        user = request.user
        task.assigned.add(user)
        task.save()
        return response.Response({'status': 'task assigned'})

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)
