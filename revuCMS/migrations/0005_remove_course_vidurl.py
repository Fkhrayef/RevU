# Generated by Django 4.2.7 on 2023-12-14 18:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('revuCMS', '0004_lesson_video'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='vidUrl',
        ),
    ]