# Generated by Django 4.2.7 on 2024-04-29 22:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tasks', '0009_remove_comment_user_remove_mention_user_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='mention',
            name='mentioned_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mentions', to=settings.AUTH_USER_MODEL),
        ),
    ]
