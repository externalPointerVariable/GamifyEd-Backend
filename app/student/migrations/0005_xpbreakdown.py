# Generated by Django 5.1.5 on 2025-03-28 16:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0004_dailymissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='XPBreakdown',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quizes_completed', models.IntegerField(default=0)),
                ('achievements_earned', models.IntegerField(default=0)),
                ('daily_logins', models.IntegerField(default=0)),
                ('total_xp', models.IntegerField(default=0)),
                ('student', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='xp_breakdown', to='student.studentprofile')),
            ],
        ),
    ]
