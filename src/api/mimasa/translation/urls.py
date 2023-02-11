from django.urls import path
from .views import MimasaCreateView, translation, get_task_status

urlpatterns = [
    path("", MimasaCreateView.as_view(), name="mimasa_application"),
    path("translation/<int:pk>", translation, name="translation"),
    path('status/<str:task_id>/', get_task_status, name='get_task_status'),
]
