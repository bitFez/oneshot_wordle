# Generated by Django 4.0.9 on 2023-05-12 15:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0004_wordshard_alter_easyguessle_attempt_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='oneshotwordeasy',
            name='clues',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='game.oneshotclueseasy'),
        ),
    ]
