# Generated by Django 4.0.9 on 2025-06-13 18:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tangle', '0003_tangleattempt_points'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='tangleattempt',
            constraint=models.UniqueConstraint(fields=('user', 'tangle'), name='unique_user_tangle'),
        ),
    ]
