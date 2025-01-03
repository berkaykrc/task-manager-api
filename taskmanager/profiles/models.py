"""
This module contains the Profile model.

Attributes:
    Profile (Model): The Profile model.
    validate_image_file_extension (function): Validate image file extension.
    create_user_profile (function): Create a profile when a new user is created.
    save_user_profile (function): Save the profile when the user is saved.
"""

from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


def validate_image_file_extension(value):
    """
    Validate image file extension.

    Args:
        value (str): The file path.

    Raises:
        ValidationError: If the file extension is not supported.

    Returns:
        None
    """

    ext = Path(value.name).suffix
    valid_extensions = [".jpg", ".png", ".jpeg", ".gif"]
    if ext.lower() not in valid_extensions:
        raise ValidationError("Unsupported file extension.")


class Profile(models.Model):
    """Profile model.

    Attributes:
        user (User): The user.
        image (Image): The profile picture.
        expo_push_token (str): The Expo push token.
    """

    user = models.OneToOneField(
        get_user_model(), on_delete=models.CASCADE, related_name="profile"
    )
    image = models.ImageField(
        upload_to="profile_pics", validators=[validate_image_file_extension]
    )
    expo_push_token = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.user.get_username()} Profile"

    def delete(self, *args, **kwargs):
        if self.image and self.image.name:
            storage, path = self.image.storage, self.image.path
            try:
                storage.delete(path)
            except (FileNotFoundError, OSError) as e:
                print(f"Error deleting file {path}: {e}")
        super().delete(*args, **kwargs)


@receiver(post_save, sender=get_user_model())
def create_user_profile(sender, instance, created, **kwargs):
    """
    Create a profile when a new user is created.

    Args:
        instance (User): The user.
        created (bool): Whether the user is created or not.

    Returns:
        None
    """
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=get_user_model())
def save_user_profile(sender, instance, **kwargs):
    """Save the profile when the user is saved.

    Args:
        instance (User): The user.

        Returns:
            None
    """
    instance.profile.save()
