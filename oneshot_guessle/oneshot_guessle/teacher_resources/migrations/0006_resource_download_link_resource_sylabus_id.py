# Generated by Django 4.0.9 on 2024-10-01 13:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teacher_resources', '0005_alter_purchase_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='resource',
            name='download_link',
            field=models.FileField(null=True, upload_to='uploads/'),
        ),
        migrations.AddField(
            model_name='resource',
            name='sylabus_id',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
