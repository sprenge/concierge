from django.db import models
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
    
class Camera(models.Model):
    name = models.CharField(max_length=255, unique=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    hostname = models.CharField(max_length=255, blank=True)
    user = models.CharField(max_length=255, blank=True)
    password = models.CharField(max_length=255, blank=True)
    services = models.ManyToManyField(CameraServices, blank=True)
    brand = models.ForeignKey('CameraType', on_delete=models.CASCADE)

class Recording(models.Model):
    camera = models.ForeignKey('Camera', on_delete=models.CASCADE)
    file_path = models.CharField(max_length=255)
    recording_date_time = models.DateTimeField() # start of the recording

FEATURE_CHOICES = [
    ('face_front', 'face_front'),
]

class RecordingFeature(models.Model):
    recording = models.ForeignKey('Recording', on_delete=models.CASCADE)
    feature_type =  models.CharField(max_length=80, choices=FEATURE_CHOICES)
    file_path = models.CharField(max_length=255)
    confirmed = models.BooleanField(default=False)
    used_for_training = models.BooleanField(default=False)
    date_time  = models.DateTimeField()
    person = models.ForeignKey(Person, blank=True, on_delete=models.CASCADE)

