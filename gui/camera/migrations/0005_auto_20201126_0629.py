# Generated by Django 3.1.3 on 2020-11-26 06:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('camera', '0004_camera_state'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recording',
            old_name='processed_by_analytics',
            new_name='video_processed_by_analytics',
        ),
        migrations.RemoveField(
            model_name='recording',
            name='file_path',
        ),
        migrations.RemoveField(
            model_name='recording',
            name='low_res_file_path',
        ),
        migrations.AddField(
            model_name='recording',
            name='file_path_snapshot',
            field=models.CharField(blank=True, max_length=512),
        ),
        migrations.AddField(
            model_name='recording',
            name='file_path_video',
            field=models.CharField(blank=True, max_length=512),
        ),
        migrations.AlterField(
            model_name='recording',
            name='duration',
            field=models.FloatField(blank=True, help_text='duration of recording in seconds'),
        ),
        migrations.AlterField(
            model_name='recording',
            name='nbr_frames',
            field=models.IntegerField(blank=True, help_text='number of video frames'),
        ),
        migrations.AlterField(
            model_name='recording',
            name='recording_date_time',
            field=models.DateTimeField(blank=True),
        ),
        migrations.AlterField(
            model_name='recording',
            name='resolution',
            field=models.CharField(blank=True, max_length=64),
        ),
    ]
