# Generated by Django 2.2.6 on 2021-09-21 19:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grader', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='submission',
            index=models.Index(fields=['-time_modified', 'id'], name='grader_subm_time_mo_43f08c_idx'),
        ),
    ]