# Generated by Django 5.1.5 on 2025-03-26 14:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0002_remove_classrooms_user_classrooms_teacher'),
    ]

    operations = [
        migrations.AddField(
            model_name='classrooms',
            name='classroom_code',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
