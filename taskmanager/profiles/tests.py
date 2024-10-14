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

from pathlib import Path

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Profile, validate_image_file_extension

User = get_user_model()


class ProfileViewSetTestCase(APITestCase):
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
        self.assertTrue(response.data['count'] > 0)
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

    def test_can_update_a_profile_with_partial_data(self):
        """
        Tests updating a profile with partial data.

        This method tests updating a profile with partial data.

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

    def test_update_profile_with_invalid_data(self):
        """
        Tests updating a profile with invalid data.

        This method tests updating a profile with invalid data.

        Args:
            self: The object itself.

        Returns:
            None.
        """
        data = {
            "user": reverse("user-detail", kwargs={"pk": self.user.pk}),
            "image": "test_image.jpeg",
            "expo_push_token": "test_token"
        }
        response = self.client.put(
            f"/profiles/{self.user.profile.id}/", data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_cannot_update_other_user_profile(self):
        """
        Tests that a user cannot update another user's profile.

        This method tests that a user cannot update another user's profile
        and receives a forbidden response.

        Args:
            self: The object itself.

        Returns:
            None.
        """
        other_user = User.objects.create_user(
            username="otheruser", password="testpassword"
        )
        data = {
            "user": reverse("user-detail", kwargs={"pk": other_user.pk}),
            "image": self.image,
            "expo_push_token": "test_token"
        }
        response = self.client.put(
            f"/profiles/{other_user.profile.id}/", data, format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

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
        self.assertEqual(response.data['message'],
                         'Profile deleted successfully.')
        self.assertEqual(response.data['profile_id'], self.user.profile.id)
        self.assertEqual(response.data['user_id'], self.user.id)

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

    def tearDown(self):
        self.client.logout()
        self.image_file.close()
        Path(self.image_file_path).unlink()
        super().tearDown()


class TestValidateImageFileExtension(TestCase):
    """
    Test case for the validate_image_file_extension function.

    This test case class contains test methods to verify the functionality of the validate_image_file_extension function.
    It includes tests for validating the file extension of an image file.
    """

    def setUp(self):
        self.image_file = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'',
            content_type='image/jpeg'
        )

    def test_valid_image_file_extension(self):
        """
        Test case for a valid image file extension.

        This test case method tests the functionality of the validate_image_file_extension function
        by passing a valid image file extension.

        It asserts that the function does not raise any exceptions.
        """
        validate_image_file_extension(self.image_file)

    def test_invalid_image_file_extension(self):
        """
        Test case for an invalid image file extension.

        This test case method tests the functionality of the validate_image_file_extension function
        by passing an invalid image file extension.

        It asserts that the function raises a ValidationError exception.
        """
        self.image_file.name = 'test_image.txt'
        with self.assertRaises(ValidationError):
            validate_image_file_extension(self.image_file)

    def tearDown(self):
        self.image_file.close()
        super().tearDown()


class GroupViewSetTestCase(APITestCase):
    """
    Test case for the GroupViewSet class.

    This test case class contains test methods to verify the functionality of GroupViewSet class.
    It includes tests for retrieving, updating, and deleting a group.
    """

    def setUp(self):
        self.user = User.objects.create(
            username="testuser", password="testuserpassword", is_staff=True)
        self.group = Group.objects.create(name="Test Group")
        self.user.groups.add(self.group)
        self.url = reverse('group-detail', kwargs={'pk': self.group.pk})
        self.client.force_authenticate(user=self.user)

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
        response = self.client.get("/profiles/groups/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_pagination(self):
        """
        Tests pagination.

        This method tests pagination.

        Args:
            self: The object itself.

        Returns:
            None.
        """
        response = self.client.get("/profiles/groups/?page=1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("results" in response.data)
        self.assertTrue("count" in response.data)
        self.assertTrue("next" in response.data)
        self.assertTrue("previous" in response.data)

    def test_only_admin_get_group(self):
        """
        Test case for the permissions of the GroupViewSet class.

        This test case method verifies that only admin users can access the GroupViewSet
        """
        response = self.client.get("/profiles/groups/")
        self.assertIn("name", response.data['results'][0])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_group(self):
        """
        Test case for updating a group.

        This test case method tests the functionality of updating a group by sending a PATCH request
        to the specified URL with the update data.

        It asserts that the response status code is 200 (OK) 
        and checks if the group's name has been successfully updated.
        """
        update_data = {'name': 'Updated Test Group'}
        response = self.client.patch(self.url, update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.group.refresh_from_db()
        self.assertEqual(self.group.name, 'Updated Test Group')

    def test_delete_group(self):
        """
        Test case to verify the deletion of a group.

        This test case method sends a DELETE request to the specified URL 
        and asserts that the response status code is 204 (NO CONTENT).
        It also asserts that the Group.DoesNotExist exception
        is raised when attempting to retrieve the group from the database.
        """
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertRaises(Group.DoesNotExist,
                          Group.objects.get, pk=self.group.pk)

    def tearDown(self):
        self.client.logout()
        super().tearDown()


class UserRegistrationTestCase(APITestCase):
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


class LoginTestCase(APITestCase):
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


class UserViewSetTestCase(APITestCase):
    """
    Test case for the UserViewSet class.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword", is_staff=True
        )
        self.client.force_authenticate(user=self.user)

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
        self.client.force_authenticate(user=None)
        response = self.client.get("/profiles/users/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_users_list(self):
        """
        Test case for listing users.

        This test case method sends a GET request to the specified URL
        and asserts that the response status code is 200 (OK).
        It also asserts that the response data contains the 'results'.
        """
        response = self.client.get("/profiles/users/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertTrue("count" in response.data)
        self.assertTrue("next" in response.data)
        self.assertTrue("previous" in response.data)

    def test_get_user(self):
        """
        Test case for retrieving a user.

        This test case method sends a GET request to the specified URL
        and asserts that the response status code is 200 (OK).
        It also asserts that the response data contains the user's username.
        """
        response = self.client.get(f"/profiles/users/{self.user.pk}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)

    def tearDown(self):
        self.client.logout()
        self.client.force_authenticate(user=None)
        super().tearDown()
