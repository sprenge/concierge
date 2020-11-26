"""gui URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers, serializers, viewsets
from camera.models import Camera, CameraListeners, CameraBrand, CameraType, Recording

class CameraBrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = CameraBrand
        fields = ['name']

class CameraTypeSerializer(serializers.ModelSerializer):
    brand = CameraBrandSerializer()
    class Meta:
        model = CameraType
        fields = ['name', 'brand']

class CameraSerializer(serializers.ModelSerializer):
    brand = CameraTypeSerializer()
    # id = serializers.Field()
    class Meta:
        model = Camera
        fields = ['id', 'name', 'ip_address', 'brand', 'user', 'password']

class RecordingSerializer(serializers.ModelSerializer):
    # camera = CameraSerializer()
    
    class Meta:
        model = Recording
        fields = ['camera', 'video_processed_by_analytics']

class CameraTypeViewSet(viewsets.ModelViewSet):
    queryset = CameraType.objects.all()
    serializer_class = CameraTypeSerializer

class CameraViewSet(viewsets.ModelViewSet):
    queryset = Camera.objects.all()
    serializer_class = CameraSerializer

class CameraListenerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CameraListeners
        fields = ['url', 'callback_type', 'description']

class CameraListenerViewSet(viewsets.ModelViewSet):
    queryset = CameraListeners.objects.all()
    serializer_class = CameraListenerSerializer

class CameraRecordingViewSet(viewsets.ModelViewSet):
    queryset = Recording.objects.all()
    serializer_class = RecordingSerializer

router = routers.DefaultRouter()
router.register(r'cameras', CameraViewSet)
router.register(r'camera_listeners', CameraListenerViewSet)
router.register(r'camera_types', CameraTypeViewSet)
router.register(r'recordings', CameraRecordingViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls'))
]