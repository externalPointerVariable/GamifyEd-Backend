# Generated by Django 5.1.5 on 2025-03-28 16:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0003_studentaipodcast'),
    ]

    operations = [
        migrations.CreateModel(
            name='DailyMissions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mission_name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('is_completed', models.BooleanField(default=False)),
                ('points', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='daily_missions', to='student.studentprofile')),
            ],
        ),
    ]
