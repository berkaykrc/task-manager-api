"""
Test cases for the projects app.

The ProjectViewSetTestCase class is a test case for the ProjectViewSet class.
It sets up the test case by creating a user, authenticating the client,
creating a profile, and creating a task.

"""

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from tasks.models import Task

from projects.models import Project

User = get_user_model()


class ProjectViewSetTestCase(APITestCase):
    """
    Test case for the ProjectViewSet class.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.client.force_authenticate(user=self.user)
        self.project = Project.objects.create(
            name="Test Project",
            description="Test Description",
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=1),
            owner=self.user,
        )
        self.project.users.add(self.user)
        self.task = Task.objects.create(
            name="Test Task",
            description="Test Description",
            priority="asap",
            status="to do",
            creator=self.user,
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=1),
            project=self.project,
        )

    def test_create_project(self):
        """
        Test case for creating a project.

        This method sends a POST request to the "/projects/" endpoint with a project
        and checks if the response status code is 201 (Created)
        and if the returned project name matches the expected value.
        """
        response = self.client.post(
            "/projects/",
            {
                "name": "Test Project 2",
                "description": "Test Description",
                "start_date": timezone.now() + timezone.timedelta(days=1),
                "end_date": timezone.now() + timezone.timedelta(days=2),
                "owner": reverse("user-detail", kwargs={"pk": self.user.pk}),
                "tasks": reverse("task-detail", kwargs={"pk": self.task.pk}),
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Test Project 2")

    def test_create_project_with_past_start_date(self):
        """
        Test case for creating a project with a past start date.

        This method sends a POST request to the "/projects/" endpoint with a project
        that has a past start date and checks if the response status code is 400 (Bad Request).
        """
        response = self.client.post(
            "/projects/",
            {
                "name": "Test Project 2",
                "description": "Test Description",
                "start_date": timezone.now() - timezone.timedelta(days=1),
                "end_date": timezone.now() + timezone.timedelta(days=2),
                "owner": reverse("user-detail", kwargs={"pk": self.user.pk}),
                "tasks": reverse("task-detail", kwargs={"pk": self.task.pk}),
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("start_date", response.data)

    def test_create_project_with_past_end_date(self):
        """
        Test case for creating a project with a past end date.

        This method sends a POST request to the "/projects/" endpoint with a project
        that has a past end date and checks if the response status code is 400 (Bad Request).
        """
        response = self.client.post(
            "/projects/",
            {
                "name": "Test Project 2",
                "description": "Test Description",
                "start_date": timezone.now() + timezone.timedelta(days=1),
                "end_date": timezone.now() - timezone.timedelta(days=1),
                "owner": reverse("user-detail", kwargs={"pk": self.user.pk}),
                "tasks": reverse("task-detail", kwargs={"pk": self.task.pk}),
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("end_date", response.data)

    def test_create_project_start_date_lte_end_date(self):
        """
        Test that creating a project cannot be created where start_date > end_date.
        """
        with self.assertRaises(IntegrityError):
            Project.objects.create(
                name="Test Project",
                description="Test Description",
                start_date=timezone.now() + timezone.timedelta(days=5),
                end_date=timezone.now() + timezone.timedelta(days=1),
                owner=self.user,
            )

    def test_project_end_date_gte_start_date(self):
        """Test that a project cannot be created where end_date < start_date."""
        with self.assertRaises(IntegrityError):
            Project.objects.create(
                name="Another Test Project",
                description="Another description",
                owner=self.user,
                start_date=timezone.now(),
                end_date=timezone.now() - timezone.timedelta(days=1),
            )

    def test_get_all_projects(self):
        """
        Test case for retrieving all projects.

        This method sends a GET request to the "/projects/" endpoint and checks if the response
        status code is 200 (OK) and if the returned project count matches the expected value.

        """
        response = self.client.get("/projects/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["name"], "Test Project")

    def test_retrieve_project(self):
        """
        Test case for retrieving a project.

        This method sends a GET request to the "/projects/1/" endpoint and checks if the response
        status code is 200 (OK) and if the returned project name matches the expected value.

        """
        response = self.client.get(f"/projects/{self.project.pk}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Test Project")

    def test_update_project(self):
        """
        Test case for updating a project.

        This method sends a PUT request to the "/projects/1/" endpoint with a project
        and checks if the response status code is 200 (OK)
        and if the returned project name matches the expected value.
        """
        response = self.client.put(
            f"/projects/{self.project.pk}/",
            {
                "name": "Updated Project",
                "description": "Test Description",
                "start_date": timezone.now() + timezone.timedelta(days=5),
                "end_date": timezone.now() + timezone.timedelta(days=10),
                "owner": reverse("user-detail", kwargs={"pk": self.user.pk}),
                "tasks": reverse("task-detail", kwargs={"pk": self.task.pk}),
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Updated Project")

    def test_delete_project(self):
        """
        Test case for deleting a project.

        This method sends a DELETE request to the "/projects/1/" endpoint and
        checks if the response status code is 204 (No Content).

        """
        response = self.client.delete(f"/projects/{self.project.pk}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
