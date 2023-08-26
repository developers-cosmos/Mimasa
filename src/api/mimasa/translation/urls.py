from django.urls import path
from .views import MimasaCreateView, translation, get_task_status, update_mimasa_instance, download_translation

urlpatterns = [
    path("", MimasaCreateView.as_view(), name="mimasa_application"),
    path("translation/<int:pk>", translation, name="translation"),
    path("get_task_status/<str:task_id>/", get_task_status, name="get_task_status"),
    path("update_mimasa_instance/<int:pk>/", update_mimasa_instance, name="update_mimasa_instance"),
    path("download/<str:file_path>/", download_translation, name="download_translation"),
]
