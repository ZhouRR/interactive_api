# Generated by Django 2.2.5 on 2019-11-14 01:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_staff_prize'),
    ]

    operations = [
        migrations.AddField(
            model_name='staff',
            name='avatar',
            field=models.CharField(blank=True, default='', max_length=200),
        ),
    ]
