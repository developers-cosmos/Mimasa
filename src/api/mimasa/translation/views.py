from celery.result import AsyncResult
from django.contrib.auth import authenticate, login
from django.http import FileResponse, Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import CreateView
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import MimasaModel, TranslationNotification
from .serializers import LoginSerializer, SignupSerializer, TranslationNotificationSerializer
from .tasks import run_translation


class MimasaCreateView(CreateView):
    model = MimasaModel
    fields = ["video", "input_language", "output_language"]
    language_choices = MimasaModel.LANGUAGE_CHOICES
    template_name = "translation/translation.html"

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.user = self.request.user
        form.save()
        return redirect("translation", form.instance.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["language_choices"] = self.language_choices
        return context


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def signup(request):
    serializer = SignupSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = authenticate(
        request,
        username=serializer.validated_data["username"],
        password=serializer.validated_data["password"],
    )
    if not user:
        return Response({"message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
    login(request, user)
    return Response({"message": "Login successful"}, status=status.HTTP_200_OK)


def get_task_status(request, task_id):
    task = AsyncResult(task_id)
    response_data = {"task_id": task_id, "task_status": task.state}
    return JsonResponse(response_data)


def update_mimasa_instance(request, pk):
    mimasa = get_object_or_404(MimasaModel, id=pk)
    mimasa.task_status = request.POST.get("status")
    mimasa.save(update_fields=["task_status", "updated_at"])
    return JsonResponse({"status": mimasa.task_status})


def download_translation(request, file_path):
    token = request.GET.get("token")
    if token:
        notification = TranslationNotification.objects.filter(download_token=token).first()
        if not notification:
            raise Http404("Invalid download token")

    try:
        return FileResponse(open(file_path, "rb"))
    except FileNotFoundError as exc:
        raise Http404("Requested file not found") from exc


def translation(request, pk):
    mimasa_instance = MimasaModel.objects.get(id=pk)
    if mimasa_instance.task_status == "CREATED":
        task_result = run_translation.delay(pk)
        mimasa_instance.task_status = task_result.status
        mimasa_instance.task_id = task_result.task_id
        mimasa_instance.save(update_fields=["task_status", "task_id", "updated_at"])

    notification = mimasa_instance.notifications.order_by("-created_at").first()
    return render(request, "translation/success.html", {"mimasa": mimasa_instance, "notification": notification})


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def list_notifications(request):
    notifications = TranslationNotification.objects.filter(user=request.user).order_by("-created_at")
    serializer = TranslationNotificationSerializer(notifications, many=True)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def mark_notification_read(request, pk):
    notification = get_object_or_404(TranslationNotification, id=pk, user=request.user)
    notification.is_read = True
    notification.save(update_fields=["is_read"])
    return Response({"message": "Notification marked as read"}, status=status.HTTP_200_OK)
