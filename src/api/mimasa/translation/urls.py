from django.urls import path

from .views import (
    MimasaCreateView,
    download_translation,
    get_task_status,
    list_notifications,
    login_view,
    mark_notification_read,
    signup,
    translation,
    update_mimasa_instance,
)

urlpatterns = [
    path("", MimasaCreateView.as_view(), name="mimasa_application"),
    path("translation/<int:pk>", translation, name="translation"),
    path("get_task_status/<str:task_id>/", get_task_status, name="get_task_status"),
    path("update_mimasa_instance/<int:pk>/", update_mimasa_instance, name="update_mimasa_instance"),
    path("download/<path:file_path>/", download_translation, name="download_translation"),
    path("auth/signup/", signup, name="signup"),
    path("auth/login/", login_view, name="login"),
    path("notifications/", list_notifications, name="list_notifications"),
    path("notifications/<int:pk>/read/", mark_notification_read, name="mark_notification_read"),
]
