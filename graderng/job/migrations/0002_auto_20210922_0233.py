# Generated by Django 2.2.6 on 2021-09-21 19:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='mossjob',
            index=models.Index(fields=['-time_created', 'id'], name='job_mossjob_time_cr_925604_idx'),
        ),
        migrations.AddIndex(
            model_name='reportjob',
            index=models.Index(fields=['-time_created', 'id'], name='job_reportj_time_cr_4a0fd4_idx'),
        ),
    ]
