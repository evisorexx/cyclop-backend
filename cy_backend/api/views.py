from django.db.models import Q
import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView
from rest_framework import serializers, generics
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.http import JsonResponse
import base64
from .models import *
from .serializers import *
from .utils import *
from django.conf import settings
from rest_framework.response import Response
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import cv2
import json
from dotenv import load_dotenv
import os 

load_dotenv()


class CustomPageNumberPagination(PageNumberPagination):
    page_size_query_param = 'size'

    def get_paginated_response(self, data):
        request = self.request
        base_url = settings.SITE_URL

        next_url = self.get_next_link()
        if next_url is not None:
            next_url = next_url.split('/api/')[-1]
        previous_url = self.get_previous_link()
        if previous_url is not None:
            previous_url = previous_url.split('/api/')[-1]

        if next_url:
            next_url = base_url + '/api/' + next_url
        if previous_url:
            previous_url = base_url + '/api/' + previous_url

        return Response({
            'count': self.page.paginator.count,
            'next': next_url,
            'previous': previous_url,
            'results': data
        })


class MainEventSerializer(serializers.ModelSerializer):
    media = serializers.SerializerMethodField()

    class Meta:
        model = MainEvent
        fields = ['id', 'media', 'time', 'is_reviewed']

    def get_media(self, obj):
        return os.environ.get('SITE_URL')+ obj.media


class MainEventViewSet(generics.ListCreateAPIView, CustomPageNumberPagination):
    pagination_class = CustomPageNumberPagination
    serializer_class = MainEventSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ['id', 'media', 'time', 'is_reviewed']
    filter_fields = ['id', 'media', 'time', 'is_reviewed']

    def get_queryset(self):
        queryset = MainEvent.objects.all()
        queryset = queryset.order_by('-time', 'id')
        return queryset


class EventTypeViewSet(generics.ListCreateAPIView, CustomPageNumberPagination):
    pagination_class = CustomPageNumberPagination
    queryset = EventType.objects.all()
    serializer_class = EventTypeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ['id', 'description']
    filter_fields = ['id', 'description']


class CameraFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model = Camera
        fields = {
            'id': ['exact'],
            'url': ['exact'],
            'is_on': ['exact'],
            'description': ['icontains'],
            'label': ['exact'],
            'markup': ['contains'],  # Adjust 'contains' based on your needs
        }
        filter_overrides = {
            ArrayField: {
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',  # Adjust 'icontains' based on your needs
                },
            },
        }

class CameraViewSet(generics.ListCreateAPIView, CustomPageNumberPagination):
    pagination_class = CustomPageNumberPagination
    queryset = Camera.objects.all()
    serializer_class = CameraSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = CameraFilter



class EventFilter(django_filters.rest_framework.FilterSet):
    boulding_box = django_filters.rest_framework.CharFilter(field_name='boulding_box', lookup_expr='exact')

    class Meta:
        model = Event
        fields = ['id', 'main_event_id', 'intruder_id', 'camera_id', 'boulding_box', 'event_type_id', 'is_confirmed']
        filter_overrides = {
            ArrayField: {
                'filter_class': django_filters.rest_framework.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'exact',
                },
            },
        }


class EventViewSet(generics.ListCreateAPIView, CustomPageNumberPagination):
    pagination_class = CustomPageNumberPagination
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = EventFilter


class IntruderViewSet(generics.ListCreateAPIView, CustomPageNumberPagination):
    pagination_class = CustomPageNumberPagination
    queryset = Intruder.objects.all()
    serializer_class = IntruderSerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]

    def get_queryset(self):
        size = self.request.query_params.getlist('size', None)
        name = self.request.query_params.get('name', None)
        id = self.request.query_params.get('id', None)
        is_query = False
        if name:
            query = Intruder.objects.filter(Q(name__contains=name) | Q(name__contains=name))
            is_query = True
        if id:
            if is_query:
                query = query & Intruder.objects.filter(id=id)
            else:
                query = Intruder.objects.filter(id=id)
                is_query = True
        if is_query == False:
            query = Intruder.objects.all()
        return query


@csrf_exempt
def draw_event(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        main_event_id = data['main_event_id']
        event_id = data['event_id']
        if main_event_id is not None and event_id is not None:
            try:
                main_event_id = int(main_event_id)
                event_id = int(event_id)
            except ValueError:
                return JsonResponse({'error': 'Invalid parameter value'})

            result = {}
            result['status'] = 1

            main_event = MainEvent.objects.filter(id=main_event_id).values()[0]
            image_path = main_event['media']
            image = cv2.imread(image_path)

            event = Event.objects.filter(id=event_id).values()[0]
            bbox = event['boulding_box']
            event_type_id = event['event_type_id_id']
            event_type = EventType.objects.filter(id=event_type_id).values()[0]['description']

            image = draw_detections(image, bbox, event_type)

            image_bytes = cv2.imencode('.png', image)[1].tobytes()

            response = HttpResponse(image_bytes, content_type='image/png')
            response['Content-Disposition'] = 'inline; filename=image.png'
            return response
        else:
            return JsonResponse({'error': 'main_event and event_id parameters are required'})
    else:
        return JsonResponse({'error': 'Invalid request method'})


@csrf_exempt
def main_event_review(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            main_event_id = data['main_event_id']
            MainEvent.objects.filter(id=main_event_id).update(is_reviewed=True)
            respose = {}
            respose['status'] = 1
            return JsonResponse(respose)
        except:
            respose = {}
            respose['status'] = 0
            return JsonResponse(respose)


@csrf_exempt
def event_confirm(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            event_id = data['event_id']
            is_confirmed = data['is_confirmed']
            Event.objects.filter(id=event_id).update(is_confirmed=bool(is_confirmed))
            respose = {}
            respose['status'] = 1
            return JsonResponse(respose)
        except:
            respose = {}
            respose['status'] = 0
            return JsonResponse(respose)


@csrf_exempt
def change_label(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            camera_id = data['camera_id']
            danger_zone = data['label']
            Camera.objects.filter(id=camera_id).update(label=danger_zone)
            respose = {}
            respose['status'] = 1
            return JsonResponse(respose)
        except:
            respose = {}
            respose['status'] = 0
            return JsonResponse(respose)


@csrf_exempt
def change_markup(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            camera_id = data['camera_id']
            markup = data['markup']
            Camera.objects.filter(id=camera_id).update(markup=markup)
            respose = {}
            respose['status'] = 1
            return JsonResponse(respose)
        except:
            respose = {}
            respose['status'] = 0
            return JsonResponse(respose)


@csrf_exempt
def capture_frame(request):
    if request.method == 'GET':
        try:
            rtsp_link = request.GET.get('rtsp_link')

            cap = cv2.VideoCapture(rtsp_link)

            if not cap.isOpened():
                response = {'status': 0, 'message': 'Failed to open RTSP stream'}
                return JsonResponse(response)

            ret, frame = cap.read()
            cap.release()

            if ret:
                _, jpeg_frame = cv2.imencode('.jpg', frame)
                encoded_frame = jpeg_frame.tobytes()
                base64_frame = base64.b64encode(encoded_frame).decode('utf-8')

                response = {'status': 1, 'frame': base64_frame}
                return JsonResponse(response)
            else:
                response = {'status': 0, 'message': 'Failed to capture frame from RTSP stream'}
                return JsonResponse(response)

        except Exception as e:
            response = {'status': 0, 'message': f'Error: {str(e)}'}
            return JsonResponse(response)

    else:
        response = {'status': 0, 'message': 'Invalid request method'}
        return JsonResponse(response)


class CountPeopleFilter(django_filters.rest_framework.FilterSet):
    list_media = django_filters.rest_framework.CharFilter(field_name='list_media', lookup_expr='exact')
    class Meta:
        model = CountPeople
        fields = ['id', 'time', 'list_media', 'people']
        filter_overrides = {
            ArrayField: {
                'filter_class': django_filters.rest_framework.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'exact',
                },
            },
        }


class CountPeopleViewSet(generics.ListCreateAPIView, CustomPageNumberPagination):
    pagination_class = CustomPageNumberPagination
    queryset = CountPeople.objects.all()
    serializer_class = CountPeopleSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = CountPeopleFilter


class ONNXFilter(django_filters.rest_framework.FilterSet):
    name = django_filters.rest_framework.CharFilter(field_name='name', lookup_expr='exact')

    class Meta:
        model = ONNX
        fields = ['id', 'name', 'description', 'path']
        filter_overrides = {
            ArrayField: {
                'filter_class': django_filters.rest_framework.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'exact',
                },
            },
        }


class UploadONNXView(APIView):
    parser_classes = MultiPartParser
    serializer_class = ONNXSerializer

    def post(self, request, format=None):
        serializer = ONNXSerializer(data=request.data)
        
        if not request.FILES:
            return Response({"error": "Файл не был передан."}, status=status.HTTP_400_BAD_REQUEST)

        file_obj = list(request.FILES.values())[0]

        file_path = os.path.join(settings.BASE_DIR, f'onnx_files/{file_obj.name}')

        if os.path.exists(file_path):
            return Response({"error": "Файл уже существует."}, status=status.HTTP_409_CONFLICT)

        if serializer.is_valid():
            with open(file_path, 'wb+') as destination:
                for chunk in file_obj.chunks():
                    destination.write(chunk)

            serializer.validated_data['path'] = file_path
            instance = serializer.save()

            response_serializer = ONNXSerializer(instance)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ONNXViewSet(generics.ListCreateAPIView, CustomPageNumberPagination):
    pagination_class = CustomPageNumberPagination
    queryset = ONNX.objects.all()
    serializer_class = ONNXSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ONNXFilter
