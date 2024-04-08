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

import os

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image
from rest_framework import status
from rest_framework.test import APIClient

from .models import Profile

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
        self.image_file_path = "test_image.jpg"
        image = Image.new("RGB", (100, 100), color="red")
        image.save(self.image_file_path)
        with open(self.image_file_path, "rb") as self.image_file:
            self.image = SimpleUploadedFile(
                name=self.image_file.name,
                content=self.image_file.read(),
                content_type='image/jpeg')
        self.client.force_authenticate(user=self.user)

    def tearDown(self):
        self.client.logout()
        self.image_file.close()
        os.remove(self.image_file_path)

    def test_authorization_is_enforced(self):
        """
        Tests authorization enforcement.

        This method tests authorization enforcement.

        Args:
            self: The object itself.

        Returns:
            None.
        """

        self.client.logout()
        response = self.client.get("/profiles/")
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

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
        self.assertTrue("image" in response.data)
        self.assertTrue("user" in response.data)

    def test_profile_created_with_new_user(self):
        """
        Tests if a profile is created when a user is created.

        This method tests the creation of a profile for a user.

        Args:
            self: The object itself.

        Returns:
            None.
        """
        self.assertTrue(Profile.objects.filter(user=self.user).exists())

    def test_can_update_a_profile(self):
        """
        Tests updating a profile.

        This method tests updating a profile.

        Args:
            self: The object itself.

        Returns:
            None.

        """
        data = {
            "user": reverse("user-detail", kwargs={"pk": self.user.pk}),
            "image": self.image,
            "expo_push_token": "test_token"
        }
        response = self.client.put(
            f"/profiles/{self.user.profile.id}/", data, format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Profile.objects.filter(user=self.user).exists())

    def test_can_delete_a_profile(self):
        """
        Tests deleting a profile.

        This method tests deleting a profile.

        Args:
            self: The object itself.

        Returns:
            None.
        """
        response = self.client.delete(f"/profiles/{self.user.profile.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Profile.objects.filter(user=self.user).exists())

    def test_set_expo_push_token(self):
        """
        Tests setting Expo push token.

        This method tests setting Expo push token.

        Args:
            self: The object itself.

        Returns:
            None.
        """
        data = {
            "expo_push_token": "test_token"
        }
        response = self.client.patch(
            f"/profiles/{self.user.profile.id}/", data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Profile.objects.filter(
            user=self.user, expo_push_token="test_token").exists())

    def test_pagination(self):
        """
        Tests pagination.

        This method tests pagination.

        Args:
            self: The object itself.

        Returns:
            None.
        """
        response = self.client.get("/profiles/?page=1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("results" in response.data)
        self.assertTrue("count" in response.data)
        self.assertTrue("next" in response.data)
        self.assertTrue("previous" in response.data)


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
        self.user = User.objects.create_user(
            username="testuser", password="testpassword", email="testuser@example.com"
        )

    def test_user_registration_successful(self):
        """
        Tests user registration.

        This method tests user registration.

        Args:
            self: The object itself.

        Returns:
            None.
        """

        response = self.client.post(
            "/register/",
            {
                "username": "test",
                "email": "test@mail.com",
                "password": "testpassword",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue("refresh" in response.data)
        self.assertTrue("access" in response.data)
        self.assertTrue(get_user_model().objects.filter(
            username="testuser").exists())

    def test_register_with_existing_username(self):
        """
        Tests user registration with an existing username.

        This method tests user registration with an existing username.

        Args:
            self: The object itself.

        Returns:
            None.
        """
        response = self.client.post(
            "/register/",
            {
                "username": self.user.username,
                "email": self.user.email,
                "password": self.user.password,
            },)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_with_existing_email(self):
        """
        Tests user registration with an existing email.

        This method tests user registration with an existing email.

        Args:
            self: The object itself.

        Returns:
            None.
        """
        response = self.client.post(
            "/register/",
            {
                "username": "testuser",
                "email": self.user.email,
                "password": "testpassword",
            },)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_with_invalid_email(self):
        """
        Tests user registration with an invalid email.

        This method tests user registration with an invalid email.

        Args:
            self: The object itself.

        Returns:
            None.
        """
        response = self.client.post(
            "/register/",
            {
                "username": "testuser",
                "email": "testmail.com",
                "password": "testpassword",
            },)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_with_invalid_data(self):
        """
        Tests user registration with invalid data.

        This method tests user registration with invalid data.

        Args:
            self: The object itself.

        Returns:
            None.
        """
        response = self.client.post(
            "/register/",
            {
                "username": "",
                "email": "notmail",
                "password": "s",
            },)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


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
            "/login/",
            {"username": "testuser", "password": "testpassword"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("access" in response.data)

    def test_login_with_invalid_credentials(self):
        """
        Tests user login with invalid credentials.

        This method tests user login with invalid credentials.

        Args:
            self: The object itself.

        Returns:
            None.
        """

        response = self.client.post(
            "/login/",
            {"username": "testuser", "password": "wrongpassword"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse("access" in response.data)

    def test_login_with_invalid_data(self):
        """
        Tests user login with invalid data.

        This method tests user login with invalid data.

        Args:
            self: The object itself.

        Returns:
            None.
        """

        response = self.client.post(
            "/login/",
            {"username": "", "password": ""},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse("access" in response.data)

    def test_login_with_non_existent_user(self):
        """
        Tests user login with a non-existent user.

        This method tests user login with a non-existent user.

        Args:
            self: The object itself.

        Returns:
            None.
        """

        response = self.client.post(
            "/login/",
            {"username": "nonexistentuser", "password": "wrongpassword"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse("access" in response.data)
