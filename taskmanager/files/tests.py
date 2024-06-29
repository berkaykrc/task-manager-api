"""
This module contains the test cases for the files app.

The test cases cover the following scenarios:
1. Test the file upload API endpoint.
2. Test the file download API endpoint.
3. Test the file sharing API endpoint.
4. Test the file deletion API endpoint.
"""

import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from projects.models import Project
from rest_framework import status
from rest_framework.test import APITestCase

from .models import SharedFile

User = get_user_model()


class FileTests(APITestCase):
    """
    Test cases for the files app.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Set up test data for the test cases.
        """
        cls.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        cls.project = Project.objects.create(
            name='testproject',
            description='testdescription',
            owner=cls.user,
            start_date='2021-01-01T00:00:00Z',
            end_date='2021-01-02T00:00:00Z'
        )
        cls.project.users.add(cls.user)
        initial_file = SimpleUploadedFile(
            "testfile.txt", b"file_content", content_type="text/plain")
        cls.file = SharedFile.objects.create(
            uploaded_by=cls.user,
            file=initial_file,
            project=cls.project
        )

    def test_file_creation(self):
        """ Test the creation of a new file. """
        shared_file = SharedFile.objects.get()
        self.assertEqual(SharedFile.objects.count(), 1)
        self.assertIn('testfile.txt', shared_file.file.name)

    def test_file_access(self):
        """ Test the access to the file. """
        response = self.client.get(
            reverse('sharedfile-detail', args=[self.file.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('testfile.txt', response.data["file"])

    def test_file_update(self):
        """ Test the update of the file. """
        updated_file = SimpleUploadedFile(
            "textfile2.txt", b"file_content", content_type="text/plain")
        response = self.client.patch(
            reverse('sharedfile-detail', args=[self.file.id]),
            {'file': updated_file},
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_file_instance = SharedFile.objects.get(id=self.file.id)
        self.assertTrue(updated_file_instance.file.name, 'textfile2.txt')

    def test_file_deletion(self):
        """ Test the deletion of the file. """
        response = self.client.delete(
            reverse('sharedfile-detail', args=[self.file.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(SharedFile.objects.count(), 0)

    def tearDown(self):
        files = SharedFile.objects.all()

        # Delete the actual files from the filesystem
        for file_instance in files:
            file_path = os.path.join(
                settings.MEDIA_ROOT, file_instance.file.name)
            if os.path.isfile(file_path):
                os.remove(file_path)

        # Delete the file instances from the database
        files.delete()

        # Call the super's tearDown to ensure any additional cleanup is performed
        super().tearDown()

        # Delete the user and project if they are not handled by the super's tearDown
        self.user.delete()
        self.project.delete()
