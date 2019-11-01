# Generated by Django 2.2.2 on 2019-11-01 05:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_activity'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProcessingStaff',
            fields=[
                ('created', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(blank=True, default='', max_length=100)),
                ('open_id', models.CharField(blank=True, default='', max_length=100)),
                ('staff_id', models.CharField(default='0000000000', max_length=10, primary_key=True, serialize=False)),
            ],
            options={
                'ordering': ('created',),
            },
        ),
    ]