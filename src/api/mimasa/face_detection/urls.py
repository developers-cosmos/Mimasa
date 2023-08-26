from django.urls import path
from .views import FaceDetectionCreateView, FaceDetectionRetrieveView

urlpatterns = [
    path("face_detection/", FaceDetectionCreateView.as_view(), name="face_detection"),
    path("face_detection/<str:task_id>/", FaceDetectionRetrieveView.as_view(), name="face_detection_results"),
]
