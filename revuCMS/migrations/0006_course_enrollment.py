# Generated by Django 4.2.7 on 2023-12-14 18:27

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('revuCMS', '0005_remove_course_vidurl'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='enrollment',
            field=models.ManyToManyField(blank=True, null=True, related_name='CourseEnrollment', to=settings.AUTH_USER_MODEL),
        ),
    ]
