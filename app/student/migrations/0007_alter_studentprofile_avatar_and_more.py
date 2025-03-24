# Generated by Django 5.1.5 on 2025-03-24 16:54

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0006_studentprofile_avatar_studentprofile_user_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentprofile',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to='student_avatars/'),
        ),
        migrations.AlterField(
            model_name='studentprofile',
            name='user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='student_profile', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='institution',
            field=models.CharField(default='Not Selected', max_length=255),
        ),
    ]
