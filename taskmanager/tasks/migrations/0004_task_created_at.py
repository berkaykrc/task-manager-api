# Generated by Django 4.2.7 on 2024-01-12 19:20

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0003_alter_task_creator_alter_task_end_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
