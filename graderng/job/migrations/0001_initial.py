# Generated by Django 2.2.6 on 2021-09-21 18:53

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MossJob',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assignment_id', models.IntegerField(help_text='Deprecated. Use assignment_id_list instead.', null=True)),
                ('assignment_id_list', models.CharField(max_length=128)),
                ('time_created', models.DateTimeField()),
                ('template', models.TextField(blank=True)),
                ('log', models.TextField()),
                ('zip_file', models.FileField(upload_to='moss/')),
                ('status', models.CharField(choices=[('P', 'Pending'), ('R', 'Running'), ('F', 'Failed'), ('D', 'Done')], default='P', max_length=2)),
                ('name', models.CharField(blank=True, max_length=128)),
            ],
            options={
                'ordering': ['-time_created'],
            },
        ),
        migrations.CreateModel(
            name='ReportJob',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('assignment_id', models.IntegerField()),
                ('time_created', models.DateTimeField()),
                ('log', models.TextField()),
                ('csv_file', models.FileField(upload_to='reports/')),
                ('status', models.CharField(choices=[('P', 'Pending'), ('R', 'Running'), ('F', 'Failed'), ('D', 'Done')], default='P', max_length=2)),
                ('name', models.CharField(blank=True, max_length=128)),
            ],
            options={
                'ordering': ['-time_created'],
            },
        ),
    ]
