# Generated by Django 4.2.7 on 2024-01-31 14:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('revuCMS', '0017_quizattempt_passed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quizattempt',
            name='score',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]