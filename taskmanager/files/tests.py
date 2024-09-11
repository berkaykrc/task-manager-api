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
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Project, SharedFile, Task

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
        cls.task = Task.objects.create(
            name="Test Task",
            description="Test Description",
            priority="asap",
            status="to do",
            creator=cls.user,
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=1),
            project=cls.project,
        )
        cls.initial_file_content = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000015 00000 n \n0000000060 00000 n \n0000000123 00000 n \n trailer\n<<\n/Root 1 0 R\n/Size 4\n>>\nstartxref\n149\n%%EOF"
        cls.initial_file = SimpleUploadedFile(
            "testfile.pdf",
            cls.initial_file_content,
            content_type="application/pdf")

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def test_create_sharedfile_success(self):
        """ Test the creation of a new file. """
        data = {
            'project': reverse('project-detail', args=[self.project.id]),
            'task': reverse('task-detail', args=[self.task.id]),
            'file': self.initial_file,
            'uploaded_by': self.user
        }
        response = self.client.post(reverse('sharedfile-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SharedFile.objects.count(), 1)
        self.assertEqual(SharedFile.objects.get().project, self.project)
        self.assertEqual(SharedFile.objects.get().task, self.task)

    def test_create_sharedfile_without_task(self):
        """ Test the creation of a new file without a task. """
        data = {
            'project': reverse('project-detail', args=[self.project.id]),
            'file': self.initial_file,
            'uploaded_by': self.user
        }
        response = self.client.post(reverse('sharedfile-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SharedFile.objects.count(), 1)
        self.assertEqual(SharedFile.objects.get().project, self.project)
        self.assertIsNone(SharedFile.objects.get().task)

    def test_create_sharedfile_missing_project(self):
        """ Test the creation of a new file without a project. """
        data = {
            'file': self.initial_file,
            'uploaded_by': self.user,
            'task': reverse('task-detail', args=[self.task.id]),
        }
        response = self.client.post(reverse('sharedfile-list'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(SharedFile.objects.count(), 0)
        self.assertIn('project', response.data)

    def test_create_sharedfile_invalid_project(self):
        """ Test the creation of a new file with an invalid project. """
        data = {
            'project': reverse('project-detail', args=[self.project.id+1]),
            'file': self.initial_file,
            'uploaded_by': self.user,
            'task': reverse('task-detail', args=[self.task.id]),
        }
        response = self.client.post(reverse('sharedfile-list'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(SharedFile.objects.count(), 0)
        self.assertIn('project', response.data)

    def test_create_sharedfile_mismatched_task_project(self):
        """ Test the creation of a new file with a mismatched task and project. """
        new_project = Project.objects.create(
            name='testproject2',
            description='testdescription',
            owner=self.user,
            start_date='2021-01-01T00:00:00Z',
            end_date='2021-01-02T00:00:00Z'
        )
        new_project.users.add(self.user)
        new_task = Task.objects.create(
            name="Test Task",
            description="Test Description",
            priority="asap",
            status="to do",
            creator=self.user,
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=1),
            project=new_project,
        )

        data = {
            'project': reverse('project-detail', args=[self.project.id]),
            # Task from different project
            'task': reverse('task-detail', args=[new_task.id]),
            'file': self.initial_file
        }
        response = self.client.post(reverse('sharedfile-list'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_file_retrive(self):
        """ Test the retrive single file. """
        file = SharedFile.objects.create(
            uploaded_by=self.user,
            file=self.initial_file.name+str(1),
            project=self.project
        )
        response = self.client.get(
            reverse('sharedfile-detail', args=[file.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('testfile.pdf', response.data["file"])

    def test_file_list(self):
        """ Test the list of files. """
        SharedFile.objects.create(
            uploaded_by=self.user,
            file=self.initial_file,
            project=self.project
        )
        SharedFile.objects.create(
            uploaded_by=self.user,
            file=self.initial_file,
            project=self.project
        )
        response = self.client.get(reverse('sharedfile-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_file_update(self):
        """ Test the update of the file. """
        file = SharedFile.objects.create(
            uploaded_by=self.user,
            file=self.initial_file,
            project=self.project
        )
        updated_file = SimpleUploadedFile(
            "textfile2.pdf", b"%PDF", content_type="application/pdf")
        response = self.client.patch(
            reverse('sharedfile-detail', args=[file.id]),
            {'file': updated_file},
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_file_instance = SharedFile.objects.get(id=file.id)
        self.assertTrue(updated_file_instance.file.name, 'textfile2.txt')

    def test_file_deletion(self):
        """ Test the deletion of the file. """
        file = SharedFile.objects.create(
            uploaded_by=self.user,
            file=self.initial_file.name+str(1),
            project=self.project
        )
        response = self.client.delete(
            reverse('sharedfile-detail', args=[file.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(SharedFile.objects.count(), 0)

    def test_valid_file_extension_and_content(self):
        """ Test the valid file extension and content. """
        with open(self.initial_file.name, 'wb') as f:
            f.write(self.initial_file_content)

        with open(self.initial_file.name, 'rb') as f:
            response = self.client.post(
                reverse('sharedfile-list'),
                {
                    'file': f,
                    'project': reverse('project-detail', args=[self.project.id])},
                format='multipart'
            )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Clean up the temporary file
        os.remove(self.initial_file.name)

    def test_invalid_file_extension(self):
        """ Test the invalid file extension. """
        invalid_file = SimpleUploadedFile(
            "testfile.exe",
            b"Hello, World!",
            content_type="text/plain")

        response = self.client.post(
            reverse('sharedfile-list'),
            {
                'file': invalid_file,
                'project': reverse('project-detail', args=[self.project.id])},
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Unsupported file extension', response.data['file'][0])

    def tearDown(self):
        files = SharedFile.objects.all()

        # Delete the actual files from the filesystem
        for file_instance in files:
            file_path = os.path.join(
                settings.MEDIA_ROOT, file_instance.file.name)
            if os.path.isfile(file_path):
                os.remove(file_path)

        super().tearDown()
