from .views import *
from django.urls import path

urlpatterns = [
    path('api/intruder/', IntruderViewSet.as_view()),
    path('api/main_events/',MainEventViewSet.as_view()),
    path('api/event_types/', EventTypeViewSet.as_view()),
    path('api/cameras/', CameraViewSet.as_view()),
    path('api/events/', EventViewSet.as_view()),
    path('api/draw_event/', draw_event),
    path('api/main_event_review/', main_event_review),
    path('api/event_confirm/', event_confirm),
    path('api/change_label/', change_label),
    path('api/change_markup/', change_markup),
    path('api/capture_frame/', capture_frame),
    path('api/countpeople/', CountPeopleViewSet.as_view()),
    path('api/upload/', UploadONNXView.as_view()),
]
