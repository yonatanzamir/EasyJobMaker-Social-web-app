# Generated by Django 3.2.6 on 2022-05-09 12:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EasyJobMakerApp', '0003_job_in_progress'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='image',
            field=models.FileField(blank=True, null=True, upload_to=''),
        ),
    ]
