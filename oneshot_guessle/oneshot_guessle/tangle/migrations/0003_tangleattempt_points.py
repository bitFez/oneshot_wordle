# Generated by Django 4.0.9 on 2025-06-13 10:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tangle', '0002_alter_tangleattempt_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='tangleattempt',
            name='points',
            field=models.IntegerField(default=0),
        ),
    ]
