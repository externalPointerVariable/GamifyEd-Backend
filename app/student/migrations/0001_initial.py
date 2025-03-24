# Generated by Django 5.1.5 on 2025-03-24 17:21

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='student_avatars/')),
                ('firstName', models.CharField(default='', max_length=255)),
                ('lastName', models.CharField(default='', max_length=255)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('institute', models.CharField(default='', max_length=255)),
                ('experience_points', models.PositiveIntegerField(default=0)),
                ('level', models.IntegerField(default=1)),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='student_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firstName', models.CharField(default='', max_length=255)),
                ('lastName', models.CharField(default='', max_length=255)),
                ('role', models.CharField(choices=[('teacher', 'Teacher'), ('student', 'Student')], max_length=10)),
                ('institution', models.CharField(default='Not Selected', max_length=255)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
