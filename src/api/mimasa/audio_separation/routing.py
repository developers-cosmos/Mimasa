from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/audio_separation/(?P<task_id>[A-Za-z0-9-]+)/$", consumers.AudioSeparationConsumer.as_asgi()),
]
