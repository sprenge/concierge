"""backenddb URL Configuration

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
from camera.models import Camera, CameraListeners, CameraBrand, CameraType, Recording, AnalyticsShapes, AnalyticsProfile, KnownObjects

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
        fields = ['id', 'name', 'host', 'brand', 'user', 'password', 'snapshot_url', 'analytics_profile']

class RecordingSerializer(serializers.ModelSerializer):
    # camera = CameraSerializer()
    # fpv = serializers.SerializerMethodField()
    
    class Meta:
        model = Recording
        fields = ['id', 'camera', 'recording_date_time', 'file_path_video', 'file_path_snapshot', 'video_processed_by_analytics', 'url_thumbnail', 'url_video', 'url_snapshot']

class AnalyticsShapesSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalyticsShapes
        fields = ['shape', 'id']

class AnalyticsProfilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalyticsProfile
        fields = ['id', 'name', 'shapes', 'min_nbr_video_frames_skipped', 'max_nbr_video_frames_skipped', 'confidence_level']

class KnownObjectsSerializer(serializers.ModelSerializer):
    class Meta:
        model = KnownObjects
        fields = ['id', 'name', 'file_path_image', 'object_type', 'identified', 'recording_id', 'frame_nbr', 'deep_learning_done']

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

class CameraRecordingViewSet(viewsets.ModelViewSet):
    queryset = Recording.objects.all()
    serializer_class = RecordingSerializer

class AnalyticsProfilesViewSet(viewsets.ModelViewSet):
    queryset = AnalyticsProfile.objects.all()
    serializer_class = AnalyticsProfilesSerializer

class AnalyticsShapesViewSet(viewsets.ModelViewSet):
    queryset = AnalyticsShapes.objects.all()
    serializer_class = AnalyticsShapesSerializer

class KnownObjectsViewSet(viewsets.ModelViewSet):
    queryset = KnownObjects.objects.all()
    serializer_class = KnownObjectsSerializer

router = routers.DefaultRouter()
router.register(r'cameras', CameraViewSet)
router.register(r'camera_listeners', CameraListenerViewSet)
router.register(r'camera_types', CameraTypeViewSet)
router.register(r'recordings', CameraRecordingViewSet)
router.register(r'analytics_profiles', AnalyticsProfilesViewSet)
router.register(r'analytics_shapes', AnalyticsShapesViewSet)
router.register(r'known_objects', KnownObjectsViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('rest/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls'))
]
