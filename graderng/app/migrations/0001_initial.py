# Generated by Django 2.2.6 on 2019-11-02 13:44

import app.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('problem_name', models.CharField(max_length=256)),
                ('assignment_id', models.IntegerField()),
                ('user_id', models.IntegerField()),
                ('content', models.TextField()),
                ('id_number', models.CharField(max_length=16)),
                ('time_limit', models.IntegerField(default=2)),
                ('memory_limit', models.IntegerField(default=256)),
                ('attempt_number', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Token',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(default=app.models.generate_token, max_length=64)),
                ('service', models.CharField(max_length=32)),
            ],
        ),
    ]
