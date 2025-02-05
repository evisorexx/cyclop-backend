from django.db import models
from datetime import datetime
from django.contrib.postgres.fields import ArrayField


class MainEvent(models.Model):
    media = models.CharField(max_length=100)
    time = models.DateTimeField(default=datetime.now())
    is_reviewed = models.BooleanField(default=False)


class Intruder(models.Model):
    name = models.CharField(max_length=100)


class EventType(models.Model):
    description = models.CharField(max_length=100)


class Camera(models.Model):
    url = models.CharField(max_length=100)
    is_on = models.BooleanField()
    description = models.CharField(max_length=100)
    label = models.CharField(max_length=100, default="")
    markup = ArrayField(models.IntegerField(), default=list)


class Event(models.Model):
    main_event_id = models.ForeignKey(MainEvent, on_delete=models.CASCADE)
    intruder_id = models.ForeignKey(Intruder, on_delete=models.CASCADE)
    camera_id = models.ForeignKey(Camera, on_delete=models.CASCADE)
    boulding_box = ArrayField(models.IntegerField(), default=list)
    event_type_id = models.ForeignKey(EventType, on_delete=models.CASCADE)
    is_confirmed = models.BooleanField(default=True)


class CountPeople(models.Model):
    time = models.DateTimeField(default=datetime.now())
    list_media = ArrayField(models.CharField(max_length=100, default=""), default=list)
    people = models.IntegerField()


class ONNX(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=500, default=None)
    path = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
