# Generated by Django 3.1.3 on 2020-12-04 06:27

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('camera', '0002_auto_20201128_1853'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnalyticsProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='AnalyticsShapes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('shape', models.CharField(max_length=128, unique=True)),
                ('description', models.CharField(blank=True, max_length=255)),
            ],
        ),
        migrations.RemoveField(
            model_name='camera',
            name='services',
        ),
        migrations.AlterField(
            model_name='recording',
            name='recording_date_time',
            field=models.DateTimeField(default=datetime.datetime(2020, 12, 4, 6, 27, 35, 726727)),
        ),
        migrations.DeleteModel(
            name='CameraServices',
        ),
        migrations.AddField(
            model_name='analyticsprofile',
            name='shapes',
            field=models.ManyToManyField(blank=True, null=True, to='camera.AnalyticsShapes'),
        ),
        migrations.AddField(
            model_name='camera',
            name='services',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='analytics_profile_name', to='camera.analyticsprofile'),
        ),
    ]
