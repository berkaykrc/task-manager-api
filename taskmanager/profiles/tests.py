from traceback import print_tb
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status

class ProfileViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)

    def test_list_profiles(self):
        response = self.client.get('/profiles/')
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_profile(self):
        profile = self.user.profile
        print(profile.id)
        response = self.client.get(f'/profiles/{profile.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)