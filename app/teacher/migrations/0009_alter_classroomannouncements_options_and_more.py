# Generated by Django 5.1.5 on 2025-03-27 16:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0008_classroomannouncements'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='classroomannouncements',
            options={},
        ),
        migrations.RemoveField(
            model_name='classroomannouncements',
            name='teacher',
        ),
    ]
