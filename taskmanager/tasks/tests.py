"""
Tests for the tasks app
"""

from django.contrib.auth import get_user_model
from django.utils import timezone
from profiles.models import Profile
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
        response = self.client.get("/tasks/1/")
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
            f"/tasks/{self.task.pk}/assign_task/", {"user_id": user2.pk})
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
                "start_date": timezone.now(),
                "end_date": timezone.now() + timezone.timedelta(days=1),
                "assigned": [self.user.pk],
                "creator": self.user,
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
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)

    def test_invalid_duratin_error(self):
        """
        Test the invalid duration error.
        """
        self.task.start_date = timezone.now() + timezone.timedelta(days=1)
        self.task.end_date = timezone.now()
        self.task.save()
        response = self.client.get(f"/tasks/{self.task.pk}/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def tearDown(self):
        """
        Clean up the data after the test case.
        """
        self.client.logout()
        self.client.force_authenticate(user=None)
        self.user.delete()
        self.profile.delete()
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

    def tearDown(self):
        """
        Clean up the data after the test case.
        """
        self.user.delete()
        self.task.delete()
