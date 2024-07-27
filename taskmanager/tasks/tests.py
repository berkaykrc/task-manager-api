"""
Tests for the tasks app
"""

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from projects.models import Project
from rest_framework import status
from rest_framework.test import APITestCase
from tasks.tasks import send_due_date_notifications

from .models import Comment, Mention, Task

User = get_user_model()


class TaskViewSetTestCase(APITestCase):
    """
    Test case for the TaskViewSet class.
    """

    def setUp(self):
        """
        Set up the necessary data for the test case.
        """
        self.owner = User.objects.create_user(
            username="owneruser", password="testpassword"
        )
        self.member = User.objects.create_user(
            username="member_user", password="testpassword"
        )
        self.non_member = User.objects.create_user(
            username="non_member_user", password="testpassword"
        )
        self.project = Project.objects.create(
            name="Test Project",
            description="Test Description",
            start_date=timezone.now() + timezone.timedelta(days=1),
            end_date=timezone.now() + timezone.timedelta(days=2),
            owner=self.owner
        )
        self.project.users.add(self.member)
        self.task = Task.objects.create(
            name="Test Task",
            description="Test Description",
            priority="asap",
            status="to do",
            creator=self.owner,
            start_date=timezone.now() + timezone.timedelta(days=1),
            end_date=timezone.now() + timezone.timedelta(days=2),
            project=self.project,
        )
        self.task.assigned.add(self.owner)
        self.client.force_authenticate(user=self.owner)

    def test_retrieve_task(self):
        """
        Test the retrieve task functionality.
        """
        response = self.client.get(f"/tasks/{self.task.pk}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Test Task")

    def test_assign_task(self):
        """
        Test the assign task functionality.
        """
        response = self.client.post(
            f"/tasks/{self.task.pk}/assign_task/", {"user_id": self.non_member.pk})
        self.task.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.non_member, self.task.assigned.all())

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
                "assigned": [self.member.pk],
                "creator": self.owner.pk,
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
                "assigned": ["invalid"],
                "creator": "invalid",
                "project": reverse("project-detail", args=[self.project.pk]),
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_remove_user_from_task(self):
        """
        Test the remove user from task functionality.
        """
        self.task.assigned.add(self.non_member)
        response = self.client.post(
            f"/tasks/{self.task.pk}/remove_user_from_task/", {"user_id": self.non_member.pk})
        self.task.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn(self.non_member, self.task.assigned.all())

    def test_remove_user_from_task_validation_error(self):
        """
        Test the remove user from task functionality with validation error.
        """
        response = self.client.post(
            f"/tasks/{self.task.pk}/remove_user_from_task/", {"user_id": "invalid"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_remove_user_from_task_non_existent_user(self):
        """
        Test the remove user from task functionality with a non-existent user.
        """
        response = self.client.post(
            f"/tasks/{self.task.pk}/remove_user_from_task/", {"user_id": 1000})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def tearDown(self):
        """
        Clean up the data after the test case.
        """
        self.client.logout()
        self.client.force_authenticate(user=None)
        super().tearDown()


class SendueDateNotificationTestCase(TestCase):
    """
    Test case for the send_due_date_notifications task.
    """

    def setUp(self):
        self.owner = User.objects.create_user(
            username="owneruser", password="testpassword"
        )
        self.member = User.objects.create_user(
            username="member_user", password="testpassword"
        )
        self.member.profile.expo_push_token = 'ExponentPushToken[yyyyyyyyyyyyyyyyyyyy]'
        self.member.profile.save()
        self.project = Project.objects.create(
            name="Test Project",
            description="Test Description",
            start_date=timezone.now() + timezone.timedelta(days=1),
            end_date=timezone.now() + timezone.timedelta(days=2),
            owner=self.owner
        )
        self.project.users.add(self.member)
        self.task = Task.objects.create(
            name="Test Task",
            description="Test Description",
            priority="asap",
            status="to do",
            creator=self.owner,
            start_date=timezone.now() + timezone.timedelta(hours=1),
            end_date=timezone.now() + timezone.timedelta(days=1),
            project=self.project,
        )
        self.task.assigned.add(self.member)
        self.client.force_login(user=self.owner)

    @patch('tasks.tasks.send_notification.delay')
    def test_send_due_date_notifications(self, mock_send_notification):
        """
        Test that the send_due_date_notifications task sends a notification to a user 
        with a task due tomorrow.
        """
        send_due_date_notifications()

        mock_send_notification.assert_called_with(
            "Task due soon",
            "The task Test Task is due tomorrow",
            self.member.profile.expo_push_token
        )


class SendNotificationOnMentionTestCase(TestCase):
    """
    Test case for the send_notification_on_mention task.
    """

    def setUp(self):
        self.owner = User.objects.create_user(
            username="owneruser", password="testpassword"
        )
        self.member = User.objects.create_user(
            username="member_user", password="testpassword"
        )
        self.member.profile.expo_push_token = 'ExponentPushToken[yyyyyyyyyyyyyyyyyyyy]'
        self.member.profile.save()
        self.project = Project.objects.create(
            name="Test Project",
            description="Test Description",
            start_date=timezone.now() + timezone.timedelta(days=1),
            end_date=timezone.now() + timezone.timedelta(days=2),
            owner=self.owner
        )
        self.project.users.add(self.member)
        self.task = Task.objects.create(
            name="Test Task",
            description="Test Description",
            priority="asap",
            status="to do",
            creator=self.owner,
            start_date=timezone.now() + timezone.timedelta(hours=1),
            end_date=timezone.now() + timezone.timedelta(days=1),
            project=self.project,
        )
        self.task.assigned.add(self.member)
        self.comment = Comment.objects.create(
            content="Test comment @member_user",
            creator=self.owner,
            task=self.task
        )
        self.mention = Mention.objects.create(
            mentioned_user=self.member,
            comment=self.comment
        )
        self.client.force_login(user=self.owner)

    @patch('tasks.tasks.send_notification.delay')
    def test_send_notification_on_mention(self, mock_send_notification):
        """
        Test that the send_notification_on_mention task sends a notification to a user 
        when they are mentioned in a comment.
        """
        self.mention = Mention.objects.create(
            mentioned_user=self.member,
            comment=self.comment
        )

        mock_send_notification.assert_called_with(
            "You have been mentioned",
            f"You have been mentioned in the task {self.task.name}",
            self.member.profile.expo_push_token
        )


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


class TaskSerializerAPITestCase(APITestCase):
    """
    Test case for the TaskSerializer class.
    """

    def setUp(self):
        """
        Set up the necessary data for the test case.
        """
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.user2 = User.objects.create_user(
            username="testuser2", password="testpassword"
        )
        self.user_outside = User.objects.create_user(
            username="testuser3", password="testpassword"
        )
        self.project = Project.objects.create(
            name="Test Project",
            description="Test Description",
            start_date=timezone.now() + timezone.timedelta(days=1),
            end_date=timezone.now() + timezone.timedelta(days=2),
            owner=self.user,
        )
        self.project.users.add(self.user, self.user2)
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
        self.client.force_authenticate(user=self.user)

    def test_validate_assigned_with_members(self):
        """
        Test the validate_assigned method with members of the project.
        """
        task_data = {
            "assigned": [self.user2.pk],
        }
        response = self.client.patch(f"/tasks/{self.task.pk}/", task_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_validate_assigned_with_non_members(self):
        """
        Test the validate_assigned method with non-members of the project.
        """
        task_data = {
            "assigned": [self.user_outside.pk],
        }
        response = self.client.patch(
            f"/tasks/{self.task.pk}/", task_data)
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)


class CommentModelTest(APITestCase):
    """
    Test case for the Comment model.
    """

    def setUp(self):
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
        self.comment = Comment.objects.create(
            task=self.task,
            creator=self.user,
            content="Test Comment @testuser",
        )

    def test_comment_creation(self):
        """
        Test the creation of the comment.
        """
        self.assertEqual(self.comment.content, "Test Comment @testuser")
        self.assertEqual(self.comment.task, self.task)
        self.assertEqual(self.comment.creator, self.user)


class CommentViewSetTest(APITestCase):
    """
    Test case for the CommentViewSet class.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword")
        self.project = Project.objects.create(
            name="Test Project",
            description="Test Description",
            start_date=timezone.now() + timezone.timedelta(days=1),
            end_date=timezone.now() + timezone.timedelta(days=2),
            owner=self.user,
        )
        self.project.users.add(self.user)
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
        self.comment = Comment.objects.create(
            content="Test comment", creator=self.user, task=self.task)
        self.client.force_authenticate(user=self.user)

    def test_create_comment(self):
        """
        Test the create comment functionality.
        """
        mentioned_user = User.objects.create_user(
            username="mentioned_user", password="testpassword"
        )
        comment_content = "New Comment @mentioned_user"
        response = self.client.post(
            "/tasks/comments/",
            {
                "content": comment_content,
                "creator": self.user.pk,
                "task": self.task.pk,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Mention.objects.filter(
            mentioned_user=mentioned_user).exists())
        self.assertTrue(Comment.objects.filter(
            content=comment_content, creator=self.user, task=self.task).exists())

    def test_non_project_member_cannot_create_comment(self):
        """
        Test that a user who is not a member of the project cannot create a comment in a task.
        """

        non_member_user = User.objects.create_user(
            username="non_member_user", password="testpassword")

        self.client.force_authenticate(user=non_member_user)

        response = self.client.post(
            "/tasks/comments/",
            {
                "content": "New Comment",
                "creator": non_member_user.pk,
                "task": self.task.pk,
                "mentions": [self.user.pk]
            },
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_mention_created_when_comment_created(self):
        """
        Test that a mention is created when a comment is created.
        """
        mentioned_user = User.objects.create_user(
            username="mentioned_user", password="testpassword"
        )
        response = self.client.post(
            "/tasks/comments/",
            {
                "content": "New Comment @mentioned_user",
                "creator": self.user.pk,
                "task": self.task.pk,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Mention.objects.filter(
            mentioned_user=mentioned_user).exists())

    def test_delete_comment_and_associated_mentions(self):
        """
        Test that when a comment is deleted, all associated mentions are also deleted.
        """
        response = self.client.delete(f'/tasks/comments/{self.comment.pk}/')
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Comment.objects.filter(pk=self.comment.pk).exists())


class MentionViewSetTest(APITestCase):
    """
    Test case for the MentionViewSet class.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword")
        self.project = Project.objects.create(
            name="Test Project",
            description="Test Description",
            start_date=timezone.now() + timezone.timedelta(days=1),
            end_date=timezone.now() + timezone.timedelta(days=2),
            owner=self.user,
        )
        self.project.users.add(self.user)
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
        self.comment = Comment.objects.create(
            content="Test comment @testuser", creator=self.user, task=self.task)
        self.mention = Mention.objects.create(
            mentioned_user=self.user, comment=self.comment)
        self.client.force_authenticate(user=self.user)

    def test_multiple_mentions_in_comment(self):
        """
        Test that multiple mentions in a comment are saved correctly.
        """
        mentioned_user1 = User.objects.create_user(
            username="mentioned_user1", password="testpassword"
        )
        mentioned_user2 = User.objects.create_user(
            username="mentioned_user2", password="testpassword"
        )
        response = self.client.post(
            "/tasks/comments/",
            {
                "content": "New Comment @mentioned_user1 @mentioned_user2",
                "creator": self.user.pk,
                "task": self.task.pk,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Mention.objects.filter(
            mentioned_user=mentioned_user1).exists())
        self.assertTrue(Mention.objects.filter(
            mentioned_user=mentioned_user2).exists())

    def test_mention_non_existent_user(self):
        """
        Test that mentions to non-existent users are not saved.
        """
        comment_content = "New Comment @non_existent_user"
        response = self.client.post(
            "/tasks/comments/",
            {
                "content": comment_content,
                "creator": self.user.pk,
                "task": self.task.pk,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(Mention.objects.filter(
            mentioned_user__username="non_existent_user").exists())

    def test_mention_without_at_symbol(self):
        """
        Test that mentions without the @ symbol are not saved.
        """
        mentioned_user = User.objects.create_user(
            username="user1", password="testpassword")
        comment_content = "Hello user1"
        response = self.client.post(
            '/tasks/comments/', {'task': self.task.pk, 'content': comment_content, 'creator': self.user.pk})
        self.assertEqual(response.status_code, 201)
        self.assertFalse(Mention.objects.filter(
            mentioned_user=mentioned_user).exists())

    def test_mention_in_middle_of_word(self):
        """
        Test that mentions in the middle of a word are not saved.
        """
        mentioned_user = User.objects.create_user(
            username="user1", password="testpassword")
        comment_content = "Hello @user1world"
        response = self.client.post(
            '/tasks/comments/', {'task': self.task.pk, 'content': comment_content, 'creator': self.user.pk})
        self.assertEqual(response.status_code, 201)
        self.assertFalse(Mention.objects.filter(
            mentioned_user=mentioned_user).exists())

    def test_mentioned_user_can_view_mention(self):
        """
        Test that the mentioned user can view the mention.
        """
        response = self.client.get(f"/tasks/mentions/{self.mention.pk}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_mentioned_user_can_edit_mention(self):
        """
        Test that the mentioned user can edit the mention.
        """
        response = self.client.patch(
            f'/tasks/mentions/{self.mention.pk}/', {'comment': 'Updated comment'})
        self.assertEqual(response.status_code, 200)

    def test_non_mentioned_user_cannot_view_mention(self):
        """
        Test that a non-mentioned user cannot view a mention.
        """
        non_mentioned_user = User.objects.create_user(
            username='non_mentioned_user', password='testpassword')
        self.client.force_authenticate(user=non_mentioned_user)
        response = self.client.get(f'/tasks/mentions/{self.mention.pk}/')
        self.assertEqual(response.status_code, 403)

    def test_non_mentioned_user_cannot_edit_mention(self):
        """
        Test that a non-mentioned user cannot edit a mention.
        """
        non_mentioned_user = User.objects.create_user(
            username='non_mentioned_user', password='testpassword')
        self.client.force_authenticate(user=non_mentioned_user)
        response = self.client.patch(
            f'/tasks/mentions/{self.mention.pk}/', {'comment': 'Updated comment'})
        self.assertEqual(response.status_code, 403)

    def test_delete_comment_and_associated_mentions(self):
        """
        Test that when a comment is deleted, all associated mentions are also deleted.
        """
        response = self.client.delete(f'/tasks/comments/{self.comment.pk}/')
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Comment.objects.filter(pk=self.comment.pk).exists())
        self.assertFalse(Mention.objects.filter(pk=self.mention.pk).exists())
