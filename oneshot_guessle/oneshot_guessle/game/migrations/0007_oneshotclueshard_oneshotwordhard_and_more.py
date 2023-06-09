# Generated by Django 4.0.9 on 2023-05-12 18:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0006_alter_easyguessle_attempt_word'),
    ]

    operations = [
        migrations.CreateModel(
            name='OneshotCluesHard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('clue1', models.CharField(max_length=6)),
                ('clue2', models.CharField(max_length=6)),
                ('clue3', models.CharField(max_length=6)),
                ('clue4', models.CharField(max_length=6)),
                ('clue5', models.CharField(max_length=6)),
                ('date', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Hard Clue',
                'verbose_name_plural': 'Hard Clues',
            },
        ),
        migrations.CreateModel(
            name='OneshotWordHard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('word', models.CharField(max_length=6)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('attempts', models.PositiveIntegerField(default=0)),
                ('correctAnswers', models.PositiveIntegerField(default=0)),
                ('clues', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='game.oneshotclueshard')),
            ],
            options={
                'verbose_name': 'Oneshot Hard Daily Word',
                'verbose_name_plural': 'Oneshot Hard Daily Words',
            },
        ),
        migrations.AlterField(
            model_name='hardguessle_attempt',
            name='word',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='game.oneshotwordhard'),
        ),
    ]
