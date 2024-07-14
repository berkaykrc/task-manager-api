# Generated by Django 4.2.7 on 2024-03-22 23:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0004_task_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='status',
            field=models.CharField(choices=[('TODO', 'To Do'), ('INPROGRESS', 'In Progress'), ('DONE', 'Done')], default='TODO', max_length=20),
        ),
    ]