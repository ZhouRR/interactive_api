# Generated by Django 2.2.5 on 2019-11-08 10:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_auto_20191104_0302'),
    ]

    operations = [
        migrations.CreateModel(
            name='Empty1',
            fields=[
                ('created', models.DateTimeField(auto_now_add=True)),
                ('id', models.CharField(default='000', max_length=3, primary_key=True, serialize=False)),
            ],
            options={
                'ordering': ('created',),
            },
        ),
    ]