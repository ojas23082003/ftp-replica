# Generated by Django 2.2.9 on 2023-09-04 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ftp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='project_image',
            field=models.FileField(blank=True, null=True, upload_to='projects'),
        ),
    ]
