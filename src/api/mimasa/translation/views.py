from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView
from .tasks import run_translation
from celery.result import AsyncResult
from django.http import JsonResponse, HttpResponse
from django.http import FileResponse

from .models import MimasaModel


class MimasaCreateView(CreateView):
    model = MimasaModel
    fields = ["video", "input_language", "output_language"]
    language_choices = MimasaModel.LANGUAGE_CHOICES
    template_name = "translation/translation.html"

    def form_valid(self, form):
        form.save()
        return redirect("translation", form.instance.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["language_choices"] = self.language_choices
        return context


def get_task_status(request, task_id):
    task = AsyncResult(task_id)
    response_data = {"task_id": task_id, "task_status": task.state}
    return JsonResponse(response_data)


def update_mimasa_instance(request, pk):
    mimasa = get_object_or_404(MimasaModel, id=pk)
    mimasa.task_status = request.POST.get("status")
    mimasa.save()
    return HttpResponse("Success")


def download_translation(request, file_path):
    return FileResponse(open(file_path, "rb"))


def translation(request, pk):
    mimasa_instance = MimasaModel.objects.get(id=pk)
    if mimasa_instance.task_status == "CREATED":
        task_result = run_translation.delay(pk)
        mimasa_instance.task_status = task_result.status
        mimasa_instance.task_id = task_result.task_id
        mimasa_instance.save()
    return render(request, "translation/success.html", {"mimasa": mimasa_instance})
