from django.contrib import admin
from camera.models import Camera
from camera.models import CameraBrand
from camera.models import CameraType
from camera.models import CameraListeners
from camera.models import Recording

class CameraBrandAdmin(admin.ModelAdmin):
    pass

class CameraTypeAdmin(admin.ModelAdmin):
    pass

class CameraListenersAdmin(admin.ModelAdmin):
    pass

class RecordingAdmin(admin.ModelAdmin):
    pass

class CameraAdmin(admin.ModelAdmin):
    model = Camera
    list_display = ['name', 'ip_address', 'hostname', 'user', 'password', 'timezone', 'state'] 
    list_editable = ['ip_address', 'hostname', 'user', 'password', 'timezone'] 

admin.site.register(Camera, CameraAdmin)
admin.site.register(CameraBrand, CameraBrandAdmin)
admin.site.register(CameraType, CameraTypeAdmin)
admin.site.register(CameraListeners, CameraListenersAdmin)
admin.site.register(Recording, RecordingAdmin)
