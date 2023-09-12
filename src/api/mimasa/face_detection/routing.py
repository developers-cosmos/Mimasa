from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/face_detection/(?P<task_id>[A-Za-z0-9-]+)/$", consumers.FaceDetectionConsumer.as_asgi()),
]
