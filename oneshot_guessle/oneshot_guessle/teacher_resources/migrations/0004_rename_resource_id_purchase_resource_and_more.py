# Generated by Django 4.0.9 on 2024-07-28 23:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('teacher_resources', '0003_alter_resource_keystage'),
    ]

    operations = [
        migrations.RenameField(
            model_name='purchase',
            old_name='resource_id',
            new_name='resource',
        ),
        migrations.AlterField(
            model_name='purchase',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
