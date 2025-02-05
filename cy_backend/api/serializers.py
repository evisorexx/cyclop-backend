from rest_framework import routers, serializers, viewsets
from .models import *
from dotenv import load_dotenv
import os 

load_dotenv()

class IntruderSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Intruder
        fields = ['id', 'name']


class MainEventSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MainEvent
        fields = ['id', 'media', 'time', 'is_reviewed']
        def get_media(self, obj):
            return os.environ.get('SITE_URL') + obj.media



class EventTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EventType
        fields = ['id', 'description']


class CameraSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Camera
        fields = ['id', 'url', 'is_on', 'description']


class EventSerializer(serializers.ModelSerializer):
    main_event_id = serializers.PrimaryKeyRelatedField(queryset=MainEvent.objects.all(), write_only=True)

    class Meta:
        model = Event
        fields = ['id', 'main_event_id', 'intruder_id', 'camera_id', 'boulding_box', 'event_type_id', 'main_event_id', 'is_confirmed']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['main_event_id'] = instance.main_event_id.id
        return representation


class CountPeopleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CountPeople
        fields = ['id', 'time', 'list_media', 'people']


class ONNXSerializer(serializers.ModelSerializer):
    class Meta:
        model = ONNX
        fields = ['id', 'name', 'description', 'path']