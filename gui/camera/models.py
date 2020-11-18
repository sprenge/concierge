import pytz
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.db import models
from person.models import Person
from timezone_field import TimeZoneField

class CameraServices(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.CharField(max_length=255, blank=True)

class CameraBrand(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name
    
class CameraType(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.CharField(max_length=255, blank=True)
    brand = models.ForeignKey('CameraBrand', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name
    
class Camera(models.Model):
    name = models.CharField(max_length=255, unique=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    hostname = models.CharField(max_length=255, blank=True)
    user = models.CharField(max_length=255, blank=True)
    password = models.CharField(max_length=255, blank=True)
    services = models.ManyToManyField(CameraServices, blank=True)
    brand = models.ForeignKey('CameraType', on_delete=models.CASCADE)
    timezone = TimeZoneField(default='Europe/Brussels')
    live_url_hd = models.CharField(max_length=512, blank=True)
    live_url_sd = models.CharField(max_length=512, blank=True)
    snapshot_url = models.CharField(max_length=512, blank=True)
    live_matrix_position = models.IntegerField(default =0, help_text="display position live feed")
    live_hdmi_port = models.IntegerField(default=99, help_text="output port (99 is none)")
    last_recording_matrix_position = models.IntegerField(default =0, help_text="display position live feed")
    last_recording_hdmi_port = models.IntegerField(default=99, help_text="output port (99 is none)")

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

@receiver(pre_save, sender=Camera)
def camera_db_changed(sender, instance, *args, **kwargs):
    print(sender, instance)

class CameraListeners(models.Model):
    ''' Callback if Camera table is changed '''
    url = models.CharField(max_length=255, unique=True)
    description = models.CharField(max_length=255, blank=True)

class Recording(models.Model):
    camera = models.ForeignKey('Camera', on_delete=models.CASCADE)
    file_path = models.CharField(max_length=255)
    recording_date_time = models.DateTimeField() # start of the recording
    duration = models.FloatField(help_text="duration of recording in seconds")
    duration = models.FloatField(help_text="duration of recording in seconds")
    nbr_frames = models.IntegerField(help_text="number of video frames")
    resolution = models.CharField(max_length=64)
    processed_by_analytics = models.BooleanField(default=False)
    low_res_file_path = models.CharField(max_length=255, blank=True)
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
