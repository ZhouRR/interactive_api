# Generated by Django 2.2.5 on 2019-11-13 02:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_prize_distribution'),
    ]

    operations = [
        migrations.AddField(
            model_name='staff',
            name='prize',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
    ]
