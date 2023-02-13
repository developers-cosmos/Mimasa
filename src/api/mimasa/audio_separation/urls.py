from django.urls import path
from .views import AudioSeparationCreateView, AudioSeparationRetrieveView

urlpatterns = [
    path("audio_separation/", AudioSeparationCreateView.as_view(), name="audio_separation"),
    path("audio_separation/<int:pk>/", AudioSeparationRetrieveView.as_view(), name="audio_separation_results"),
]
