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
from camera.models import Camera, CameraListeners

class CameraSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Camera
        fields = ['name', 'user', 'password', 'ip_address']

class CameraViewSet(viewsets.ModelViewSet):
    queryset = Camera.objects.all()
    serializer_class = CameraSerializer

class CameraListenerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CameraListeners
        fields = ['url', 'description']

class CameraListenerViewSet(viewsets.ModelViewSet):
    queryset = CameraListeners.objects.all()
    serializer_class = CameraListenerSerializer

router = routers.DefaultRouter()
router.register(r'cameras', CameraViewSet)
router.register(r'camera_listeners', CameraListenerViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls'))
]