# Generated by Django 2.2.5 on 2019-11-19 05:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_staff_isbse'),
    ]

    operations = [
        migrations.RenameField(
            model_name='staff',
            old_name='isBse',
            new_name='is_bse',
        ),
    ]
