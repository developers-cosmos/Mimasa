from django.shortcuts import render, redirect
from django.views.generic import CreateView
from .tasks import async_process
from celery.result import AsyncResult
from django.http import JsonResponse

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
    response_data = {'task_id': task_id, 'task_status': task.state}
    return JsonResponse(response_data)

def translation(request, pk):
    global mimasa_instance
    mimasa_instance = MimasaModel.objects.get(id=pk)
    if request.method == 'POST' or True:
        task_result = async_process.delay(pk)
        mimasa_instance.task_status = task_result.status
        mimasa_instance.task_id = task_result.task_id
        mimasa_instance.save()
    return render(request, "translation/success.html", {"mimasa": mimasa_instance})
