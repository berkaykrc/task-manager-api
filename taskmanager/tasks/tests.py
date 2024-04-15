"""
Tests for the tasks app
"""

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from projects.models import Project
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Task

User = get_user_model()


class TaskViewSetTestCase(APITestCase):
    """
    Test case for the TaskViewSet class.
    """

    def setUp(self):
        """
        Set up the necessary data for the test case.
        """
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.client.force_authenticate(user=self.user)
        self.project = Project.objects.create(
            name="Test Project",
            description="Test Description",
            start_date=timezone.now() + timezone.timedelta(days=1),
            end_date=timezone.now() + timezone.timedelta(days=2),
            owner=self.user
        )
        self.task = Task.objects.create(
            name="Test Task",
            description="Test Description",
            priority="asap",
            status="to do",
            creator=self.user,
            start_date=timezone.now() + timezone.timedelta(days=1),
            end_date=timezone.now() + timezone.timedelta(days=2),
            project=self.project,
        )
        self.task.assigned.add(self.user)

    def test_retrieve_task(self):
        """
        Test the retrieve task functionality.
        """
        response = self.client.get(f"/tasks/{self.task.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Test Task")

    def test_assign_task(self):
        """
        Test the assign task functionality.
        """
        user2 = User.objects.create_user(
            username="testuser2", password="testpassword"
        )
        response = self.client.post(
            f"/tasks/{self.task.id}/assign_task/", {"user_id": user2.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertIn(user2, self.task.assigned.all())

    def test_create_task(self):
        """
        Test the create task functionality.
        """
        response = self.client.post(
            "/tasks/",
            {
                "name": "New Task",
                "description": "New Description",
                "priority": "ASAP",
                "status": "TODO",
                "start_date": timezone.now() + timezone.timedelta(days=1),
                "end_date": timezone.now() + timezone.timedelta(days=2),
                "assigned": [self.user.pk],
                "creator": self.user.pk,
                "project": reverse("project-detail", args=[self.project.pk]),
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_task_validation_error(self):
        """
        Test the create task functionality with validation error.
        """
        response = self.client.post(
            "/tasks/",
            {
                "name": "",
                "description": "",
                "priority": "invalid",
                "status": "invalid",
                "start_date": timezone.now() + timezone.timedelta(days=1),
                "end_date": timezone.now() - timezone.timedelta(days=2),
                "assigned": "invalid",
                "creator": "invalid",
                "project": "invalid",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def tearDown(self):
        """
        Clean up the data after the test case.
        """
        self.client.logout()
        self.client.force_authenticate(user=None)
        self.user.delete()
        self.project.delete()
        self.task.delete()


class TaskModelTest(APITestCase):
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
        self.project = Project.objects.create(
            name="Test Project",
            description="Test Description",
            start_date=timezone.now() + timezone.timedelta(days=1),
            end_date=timezone.now() + timezone.timedelta(days=2),
            owner=self.user,
        )
        self.task = Task.objects.create(
            name="Test Task",
            start_date=timezone.now() + timezone.timedelta(days=1),
            end_date=timezone.now() + timezone.timedelta(days=2),
            description="Test description",
            priority="MEDIUM",
            status="TODO",
            creator=self.user,
            project=self.project,
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

    def tearDown(self):
        """
        Clean up the data after the test case.
        """
        self.user.delete()
        self.task.delete()
        self.project.delete()
