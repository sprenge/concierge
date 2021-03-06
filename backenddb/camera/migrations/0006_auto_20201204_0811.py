# Generated by Django 3.1.3 on 2020-12-04 08:11

import datetime
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('camera', '0005_auto_20201204_0757'),
    ]

    operations = [
        migrations.AddField(
            model_name='analyticsprofile',
            name='confidence_level',
            field=models.IntegerField(default=70, help_text='Confidence level on detect objects, increase if too many false positive are detected', validators=[django.core.validators.MaxValueValidator(100), django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AddField(
            model_name='analyticsprofile',
            name='max_nbr_video_frames_skipped',
            field=models.IntegerField(default=60, help_text='maximum number of frames skipped during video analytics'),
        ),
        migrations.AlterField(
            model_name='analyticsprofile',
            name='min_nbr_video_frames_skipped',
            field=models.IntegerField(default=5, help_text='minimum number of frames skipped during video analytics'),
        ),
        migrations.AlterField(
            model_name='recording',
            name='recording_date_time',
            field=models.DateTimeField(default=datetime.datetime(2020, 12, 4, 8, 11, 9, 674661)),
        ),
    ]
