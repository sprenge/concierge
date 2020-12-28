import pytz
from datetime import datetime
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.db import models
from person.models import Person
from timezone_field import TimeZoneField
import requests
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.safestring import mark_safe

try:
    cia = os.environ['CONCIERGE_IP_ADDRESS']
except:
    cia = '127.0.0.1'
print("CONCIERGE_IP_ADDRESS backenddb %s", cia)

def validate_not_underscore(value):
    if '_' in value:
        raise ValidationError(
            _('%(value)s contains underscore(s), this is not allowed'),
            params={'value': value},
        )

isalphavalidator = RegexValidator(r'[A-z0-9]+', message='name must be alphanumeric', code='Invalid name')

valid = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789')
def test_camera_name(s):
    return set(s).issubset(valid)

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
    name = models.CharField(max_length=255, validators=[validate_not_underscore], unique=True)
    host = models.GenericIPAddressField(blank=True, null=True)
    user = models.CharField(max_length=255, blank=True)
    password = models.CharField(max_length=255, blank=True)
    analytics_profile = models.ForeignKey('AnalyticsProfile', blank=True, null=True, on_delete=models.CASCADE, related_name='analytics_profile_name')
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
    # if not test_camera_name(instance.name):
    #    raise Exception("No underscore allowed in the name")
    payload = {
        "name": instance.name, 
        "host": instance.host,
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
    file_path_video = models.CharField(max_length=512, unique=True)
    file_path_snapshot = models.CharField(max_length=512, blank=True)
    url_video = models.URLField(null=True, blank=True)
    url_snapshot = models.URLField(null=True, blank=True)
    url_thumbnail = models.URLField(null=True, blank=True)
    recording_date_time = models.DateTimeField(default=datetime.now()) # start of the recording
    duration = models.FloatField(blank=True, null=True, help_text="duration of recording in seconds")
    nbr_frames = models.IntegerField(blank=True, null=True, help_text="number of video frames")
    resolution = models.CharField(blank=True, max_length=64)
    video_processed_by_analytics = models.BooleanField(default=False)

    @property
    def full_video_path(self):
        return "http://{}:8000".format(cia)+self.file_path_video
    
    def image_img(self):
        if self.url_thumbnail:
            return mark_safe('<img class="thumbnail" src="{}" />'.format(self.url_thumbnail))
        else:
            return '(Sin imagen)'
        image_img.short_description = 'Thumb'

    def play_video(self):
        if self.url_video:
            return mark_safe('<video poster="{}" preload="none" width="200" controls autoplay><source src="{}" type="video/mp4"></source></video>'.format(self.url_thumbnail, self.url_video))
        else:
            return '(Sin imagen)'
        play_video.short_description = 'Thumb'

    def __str__(self):
        return self.file_path_video

class AnalyticsShapes(models.Model):
    shape = models.CharField(max_length=128, unique=True)
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.shape

class AnalyticsProfile(models.Model):
    name = models.CharField(max_length=128, unique=True)
    shapes = models.ManyToManyField('AnalyticsShapes', null=True, blank=True)
    min_nbr_video_frames_skipped = models.IntegerField(default=5, help_text="minimum number of frames skipped during video analytics")
    max_nbr_video_frames_skipped = models.IntegerField(default=60, help_text="maximum number of frames skipped during video analytics")
    confidence_level = models.IntegerField(
        default=70,
        help_text = 'Confidence level on detect objects, increase if too many false positive are detected',
        validators=[
            MaxValueValidator(100),
            MinValueValidator(1)
        ]
     )
    def __str__(self):
        return self.name


class KnownObjects(models.Model):
    name = models.CharField(max_length=256, blank=True)
    file_path_image = models.CharField(max_length=512, unique=True)
    object_type = models.ForeignKey('AnalyticsShapes', null=True, blank=True, on_delete=models.CASCADE)
    identified = models.BooleanField(default=True, help_text="Set to False for instance if a person is not identified yet")
    deep_learning_done = models.BooleanField(default=False, help_text="Set to True if deep learing processing is finished")
    recording_id = models.CharField(max_length=256, blank=True)
    frame_nbr = models.CharField(max_length=256, blank=True)

    def __str__(self):
        return self.name
