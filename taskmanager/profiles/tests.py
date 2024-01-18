"""
Test cases for the profiles app.

Test cases:
    - List profiles
    - Retrieve profile
    - User registration
    - User login
    
    
To run the tests:
    python manage.py test profiles
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


class ProfileViewSetTestCase(TestCase):
    """
    Profile view set test case.

    This class contains the test cases for the Profile view set.

    Attributes:
        client (APIClient): The API client.
        user (User): The user.

        Methods:
            setUp: Prepares the test case.
            test_list_profiles: Tests listing profiles.
            test_retrieve_profile: Tests retrieving a profile.
    """

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.client.force_authenticate(user=self.user)

    def test_list_profiles(self):
        """
        Tests listing profiles.

        This method tests listing profiles.

        Args:
            self: The object itself.

        Returns:
            None.
        """

        response = self.client.get("/profiles/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_profile(self):
        """
        Tests retrieving a profile.

        This method tests retrieving a profile.

        Args:
            self: The object itself.

        Returns:
            None.
        """
        profile = self.user.profile
        response = self.client.get(f"/profiles/{profile.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


# write test for user registration and login


class UserRegistrationTestCase(TestCase):
    """
    User registration test case.

    This class contains the test cases for user registration.

    Attributes:
        client (APIClient): The API client.
        user (User): The user.

        Methods:
            setUp: Prepares the test case.
            test_user_registration: Tests user registration.
    """

    def setUp(self):
        self.client = APIClient()

    def test_user_registration(self):
        """
        Tests user registration.

        This method tests user registration.

        Args:
            self: The object itself.

        Returns:
            None.
        """

        response = self.client.post(
            "/profiles/register/",
            {
                "username": "testuser",
                "email": "test@mail.com",
                "password": "testpassword",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class LoginTestCase(TestCase):
    """
    Login test case.

    This class contains the test cases for user login.

    Attributes:
        client (APIClient): The API client.
        user (User): The user.

        Methods:
            setUp: Prepares the test case.
            test_login: Tests user login.
    """

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )

    def test_login(self):
        """
        Tests user login.

        This method tests user login.

        Args:
            self: The object itself.

        Returns:
            None.
        """

        response = self.client.post(
            "/profiles/login/",
            {"username": "testuser", "password": "testpassword"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
