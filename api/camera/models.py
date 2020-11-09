from django.db import models
from django.core import validators
from person.models import Person

class CameraServices(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.CharField(max_length=255, blank=True)

class CameraBrand(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.CharField(max_length=255, blank=True)
    
class CameraType(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.CharField(max_length=255)
    brand = models.ForeignKey('CameraBrand', on_delete=models.CASCADE)
    
regex = r'^[A-z][-][\d+]$'
class Camera(models.Model):
    name = models.CharField(max_length=255, unique=True, validators=[validators.RegexValidator(regex)])
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    hostname = models.CharField(max_length=255, blank=True)
    user = models.CharField(max_length=255, blank=True)
    password = models.CharField(max_length=255, blank=True)
    services = models.ManyToManyField(CameraServices, blank=True)
    brand = models.ForeignKey('CameraType', on_delete=models.CASCADE)
    live_matrix_position = models.IntegerField(default =0, help_text="display position live feed")
    live_hdmi_port = models.IntegerField(default=99, help_text="output port (99 is none)")
    last_recording_matrix_position = models.IntegerField(default =0, help_text="display position live feed")
    last_recording_hdmi_port = models.IntegerField(default=99, help_text="output port (99 is none)")

class Recording(models.Model):
    camera = models.ForeignKey('Camera', on_delete=models.CASCADE)
    file_path = models.CharField(max_length=255)
    recording_date_time = models.DateTimeField() # start of the recording
    duration = models.FloatField(help_text="duration of recording in seconds")
    duration = models.FloatField(help_text="duration of recording in seconds")
    nbr_frames = models.IntegerField(help_text="number of video frames")
    resolution = models.CharField(max_length=64)
    processed_by_analytics = models.BooleanField(default=False)

'''
FEATURE_CHOICES = [
    ('face_front', 'face_front'),
]

#class RecordingFeature(models.Model):
    recording = models.ForeignKey('Recording', on_delete=models.CASCADE)
    feature_type =  models.CharField(max_length=80, choices=FEATURE_CHOICES)
    file_path = models.CharField(max_length=255)
    confirmed = models.BooleanField(default=False)
    used_for_training = models.BooleanField(default=False)
    date_time  = models.DateTimeField()
    person = models.ForeignKey(Person, blank=True, on_delete=models.CASCADE)
'''
