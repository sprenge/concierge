from django.contrib import admin
from camera.models import Camera
from camera.models import CameraBrand
from camera.models import CameraType
from camera.models import CameraListeners
from camera.models import Recording
from camera.models import AnalyticsProfile
from camera.models import AnalyticsShapes
from django.contrib.admin import DateFieldListFilter

class CameraBrandAdmin(admin.ModelAdmin):
    pass

class CameraTypeAdmin(admin.ModelAdmin):
    pass

class CameraListenersAdmin(admin.ModelAdmin):
    pass

class RecordingAdmin(admin.ModelAdmin):
    model = Recording
    show_change_link = True
    list_filter = (
        ('recording_date_time', DateFieldListFilter), 'camera',
    )
    list_display = ['camera', 'recording_date_time',"play_video"]
    read_only = ['image_img',]

class AnalyticsProfileAdmin(admin.ModelAdmin):
    pass

class AnalyticsShapesAdmin(admin.ModelAdmin):
    pass

class CameraAdmin(admin.ModelAdmin):
    model = Camera
    list_display = ['name', 'host', 'user', 'password', 'timezone', 'state'] 
    list_editable = ['host', 'user', 'password', 'timezone'] 

admin.site.register(Camera, CameraAdmin)
admin.site.register(CameraBrand, CameraBrandAdmin)
admin.site.register(CameraType, CameraTypeAdmin)
admin.site.register(CameraListeners, CameraListenersAdmin)
admin.site.register(Recording, RecordingAdmin)
admin.site.register(AnalyticsProfile, AnalyticsProfileAdmin)
admin.site.register(AnalyticsShapes, AnalyticsShapesAdmin)
