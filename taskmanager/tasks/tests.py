"""
Tests for the tasks app
"""

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone
from profiles.models import Profile
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from .models import Task
from .views import TaskViewSet


class TaskViewSetTestCase(TestCase):
    """
    Test case for the TaskViewSet class.
    """

    def setUp(self):
        """
        Set up the necessary data for the test case.
        """
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.profile, created = Profile.objects.get_or_create(user=self.user)
        if created:
            self.profile.image = (
                r"taskmanager\\media\\profile_pics\\LostArk_Creator_shadow.png"
            )
            self.profile.save()
        self.task = Task.objects.create(
            name="Test Task",
            description="Test Description",
            priority="asap",
            status="to do",
            creator=self.user,
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=1),
        )

    def test_retrieve_task(self):
        """
        Test the retrieve task functionality.
        """
        view = TaskViewSet.as_view({"get": "retrieve"})
        request = self.factory.get("/tasks/1/")
        force_authenticate(request, user=self.user)
        response = view(request, pk=self.task.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Test Task")

    def test_assign_task(self):
        """
        Test the assign task functionality.
        """
        view = TaskViewSet.as_view({"post": "assign_task"})
        request = self.factory.post(f"/tasks/{self.task.pk}/assign_task/")
        force_authenticate(request, user=self.user)
        response = view(request, pk=self.task.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertIn(self.user, self.task.assigned.all())

    def test_create_task(self):
        """
        Test the create task functionality.
        """
        view = TaskViewSet.as_view({"post": "create"})
        request = self.factory.post(
            "/tasks/",
            {
                "name": "New Task",
                "description": "New Description",
                "priority": "ASAP",
                "status": "TODO",
                "start_date": timezone.now(),
                "end_date": timezone.now() + timezone.timedelta(days=1),
                "assigned": [self.user.pk],
                "creator": self.user,
            },
        )
        force_authenticate(request, user=self.user)
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_task_validation_error(self):
        """
        Test the create task functionality with validation error.
        """
        view = TaskViewSet.as_view({"post": "create"})
        request = self.factory.post(
            "/tasks/",
            {
                "name": "New Task",
                "description": "New Description",
                "priority": "ASAP",
                "status": "TODO",
                "start_date": timezone.now(),
                "end_date": timezone.now() - timezone.timedelta(days=1),
                "assigned": [self.user.pk],
                "creator": self.user,
            },
        )
        force_authenticate(request, user=self.user)
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)

    def test_invalid_duratin_error(self):
        """
        Test the invalid duration error.
        """
        view = TaskViewSet.as_view({"get": "retrieve"})
        self.task.start_date = timezone.now() + timezone.timedelta(days=1)
        self.task.end_date = timezone.now()
        self.task.save()
        request = self.factory.get(f"/tasks/{self.task.pk}/")
        force_authenticate(request, user=self.user)
        response = view(request, pk=self.task.pk)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)


class TaskModelTest(TestCase):
    """
    Test case for the Task model.
    """

    def setUp(self):
        """
        Set up the necessary data for the test case.
        """
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.task = Task.objects.create(
            name="Test Task",
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=1),
            description="Test description",
            priority="MEDIUM",
            status="TODO",
            creator=self.user,
        )
        self.task.assigned.add(self.user)

    def test_duration_property(self):
        """
        Test the duration property of the Task model.
        """
        self.assertEqual(self.task.duration, "24h 0m")

    def test_str_method(self):
        """
        Test the __str__ method of the Task model.
        """
        self.assertEqual(str(self.task), "Test Task")

    def test_invalid_duration(self):
        """
        Test the invalid duration error of the Task model.
        """
        self.task.start_date = timezone.now() + timezone.timedelta(days=1)
        self.task.end_date = timezone.now()
        self.assertEqual(
            self.task.duration, "Error: End date is earlier than start date"
        )

    def test_missing_dates(self):
        """
        Test the missing dates error of the Task model.
        """
        self.task.start_date = None
        self.task.end_date = None
        self.assertEqual(
            self.task.duration, "Error: start_date and/or end_date is not set"
        )

    def test_assigned_users(self):
        """
        Test the assigned users of the Task model.
        """
        self.assertEqual(self.task.assigned.count(), 1)
        self.assertEqual(self.task.assigned.first(), self.user)

    def test_creator(self):
        """
        Test the creator of the Task model.
        """
        self.assertEqual(self.task.creator, self.user)
