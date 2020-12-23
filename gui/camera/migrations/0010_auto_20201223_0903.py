# Generated by Django 3.1.4 on 2020-12-23 09:03

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('camera', '0009_auto_20201211_1144'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recording',
            name='recording_date_time',
            field=models.DateTimeField(default=datetime.datetime(2020, 12, 23, 9, 3, 53, 170623)),
        ),
        migrations.CreateModel(
            name='KnownObjects',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=256)),
                ('file_path_image', models.CharField(max_length=512)),
                ('identified', models.BooleanField(default=True, help_text='Set to False for instance if a person is not identified yet')),
                ('recording_id', models.CharField(blank=True, max_length=256)),
                ('frame_nbr', models.CharField(blank=True, max_length=256)),
                ('object_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='camera.analyticsshapes')),
            ],
        ),
    ]
