# Generated by Django 4.2.7 on 2024-01-17 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('revuCMS', '0007_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='firstName',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='lastName',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]
