# Generated by Django 2.2.5 on 2019-11-19 07:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0012_auto_20191119_0509'),
    ]

    operations = [
        migrations.AddField(
            model_name='processingstaff',
            name='is_bse',
            field=models.BooleanField(default=False),
        ),
    ]