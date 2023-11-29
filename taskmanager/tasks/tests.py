from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework import status
from .views import TaskViewSet
from .models import Task
from profiles.models import Profile
from django.utils import timezone


class TaskViewSetTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username='testuser', password='testpassword')
        self.profile, created = Profile.objects.get_or_create(user=self.user)
        if created:
            self.profile.image = 'taskmanager\media\profile_pics\LostArk_Creator_shadow.png'
            self.profile.save()
        self.task = Task.objects.create(
            name='Test Task',
            description='Test Description',
            priority='asap',
            status='to do',
            creator=self.user,
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=1)
        )

    def test_retrieve_task(self):
        view = TaskViewSet.as_view({'get': 'retrieve'})
        request = self.factory.get('/tasks/1/')
        force_authenticate(request, user=self.user)
        response = view(request, pk=self.task.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Task')

    def test_assign_task(self):
        view = TaskViewSet.as_view({'post': 'assign_task'})
        request = self.factory.post(f'/tasks/{self.task.pk}/assign_task/')
        force_authenticate(request, user=self.user)
        response = view(request, pk=self.task.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertIn(self.user, self.task.assigned.all())

    def test_create_task(self):
        view = TaskViewSet.as_view({'post': 'create'})
        request = self.factory.post(
            '/tasks/', {
                'name': 'New Task',
                'description': 'New Description',
                'priority': 'ASAP',
                'status': 'TODO',
                'start_date': timezone.now(),
                'end_date': timezone.now() + timezone.timedelta(days=1),
                'assigned': [self.user.pk],
                'creator': self.user.pk
            }
        )
        force_authenticate(request, user=self.user)
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class TaskModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpassword')
        self.task = Task.objects.create(
            name='Test Task',
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=1),
            description='Test description',
            priority='MEDIUM',
            status='TODO',
            creator=self.user
        )
        self.task.assigned.add(self.user)

    def test_duration_property(self):
        self.assertEqual(self.task.duration, '24h 0m')

    def test_str_method(self):
        self.assertEqual(str(self.task), 'Test Task')

    def test_invalid_duration(self):
        self.task.start_date = timezone.now() + timezone.timedelta(days=1)
        self.task.end_date = timezone.now()
        self.assertEqual(
            self.task.duration, 'Error: End date is earlier than start date')

    def test_missing_dates(self):
        self.task.start_date = None
        self.task.end_date = None
        self.assertEqual(
            self.task.duration, 'Error: start_date and/or end_date is not set')

    def test_assigned_users(self):
        self.assertEqual(self.task.assigned.count(), 1)
        self.assertEqual(self.task.assigned.first(), self.user)

    def test_creator(self):
        self.assertEqual(self.task.creator, self.user)
