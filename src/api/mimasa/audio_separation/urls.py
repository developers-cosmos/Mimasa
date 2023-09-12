from django.urls import path

from .views import AudioSeparationCreateView, AudioSeparationRetrieveView

urlpatterns = [
    path("audio_separation/", AudioSeparationCreateView.as_view(), name="audio_separation"),
    path("audio_separation/<str:task_id>/", AudioSeparationRetrieveView.as_view(), name="audio_separation_results"),
]
