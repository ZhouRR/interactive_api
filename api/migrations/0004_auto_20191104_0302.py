# Generated by Django 2.2.2 on 2019-11-04 03:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_processingstaff'),
    ]

    operations = [
        migrations.CreateModel(
            name='Prize',
            fields=[
                ('created', models.DateTimeField(auto_now_add=True)),
                ('prize_id', models.CharField(default='000', max_length=3, primary_key=True, serialize=False)),
                ('prize_name', models.CharField(blank=True, default='', max_length=100)),
                ('prize_memo', models.CharField(blank=True, default='', max_length=200)),
            ],
            options={
                'ordering': ('created',),
            },
        ),
        migrations.AddField(
            model_name='activity',
            name='prize',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
    ]