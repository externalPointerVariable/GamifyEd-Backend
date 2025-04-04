# Generated by Django 5.1.5 on 2025-03-26 15:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0001_initial'),
        ('teacher', '0005_alter_classrooms_classroom_code'),
    ]

    operations = [
        migrations.CreateModel(
            name='JoinedClassrooms',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('joined_at', models.DateTimeField(auto_now_add=True)),
                ('classroom', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='joined_students', to='teacher.classrooms')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='joined_classrooms', to='student.studentprofile')),
            ],
            options={
                'unique_together': {('student', 'classroom')},
            },
        ),
    ]
