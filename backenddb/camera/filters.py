import django_filters
from .models import Recordings

class RecordingsFilter(django_filters.FilterSet):
    class Meta:
        model = Recordings
        fields = '__all__'