import pytz
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.db import models
from person.models import Person
from timezone_field import TimeZoneField
import requests


valid = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789')
def test_camera_name(s):
    return set(s).issubset(valid)

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
    brand = models.ForeignKey('CameraType', on_delete=models.CASCADE, related_name="camera_type")
    timezone = TimeZoneField(default='Europe/Brussels')
    live_url_hd = models.CharField(max_length=512, blank=True)
    live_url_sd = models.CharField(max_length=512, blank=True)
    snapshot_url = models.CharField(max_length=512, blank=True)
    live_matrix_position = models.IntegerField(default =0, help_text="display position live feed")
    live_hdmi_port = models.IntegerField(default=99, help_text="output port (99 is none)")
    last_recording_matrix_position = models.IntegerField(default =0, help_text="display position live feed")
    last_recording_hdmi_port = models.IntegerField(default=99, help_text="output port (99 is none)")
    state = models.CharField(max_length=16, default = "NOK")

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

@receiver(pre_save, sender=Camera)
def camera_db_changed(sender, instance, *args, **kwargs):
    if not test_camera_name(instance.name):
        raise Exception("No underscore allowed in the name")
    payload = {
        "name": instance.name, 
        "ip_address": instance.ip_address,
        "user": instance.user,
        "password": instance.password,
        "brand": instance.brand.brand.name,
        "timezone": -3600,
    }
    listeners = CameraListeners.objects.filter(callback_type="config")
    for listener in listeners:
        try:
            r = requests.post(listener.url, json=payload, timeout=5)
            if r.status_code == 201:
                instance.state = "OK"
                ret_payload = r.json()
                if 'live_url_hd' in ret_payload:
                    instance.live_url_hd = ret_payload['live_url_hd']
                if 'live_url_sd' in ret_payload:
                    instance.live_url_sd = ret_payload['live_url_sd']
                if 'snapshot_url' in ret_payload:
                    instance.snapshot_url = ret_payload['snapshot_url']
            else:
                instance.state = "NOK"
        except Exception as e:
            instance.state = "NOK"
            print(e)

class CameraListeners(models.Model):
    ''' Callback if Camera table is changed '''
    url = models.CharField(max_length=255, unique=True)
    callback_type = models.CharField(max_length=32, default='ftp')
    description = models.CharField(max_length=255, blank=True)

class Recording(models.Model):
    camera = models.ForeignKey('Camera', on_delete=models.CASCADE)
    file_path_video = models.CharField(max_length=512, blank=True)
    file_path_snapshot = models.CharField(max_length=512, blank=True)
    recording_date_time = models.DateTimeField(blank=True, null=True) # start of the recording
    duration = models.FloatField(blank=True, null=True, help_text="duration of recording in seconds")
    nbr_frames = models.IntegerField(blank=True, null=True, help_text="number of video frames")
    resolution = models.CharField(blank=True, max_length=64)
    video_processed_by_analytics = models.BooleanField(default=False)
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
