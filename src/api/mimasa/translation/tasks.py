from .models import MimasaModel
from mimasa.celery import app
from django.core.files import File


@app.task
def async_process(pk):
    print(f"Processing {pk}...")
    mimasa_instance = MimasaModel.objects.get(id=pk)
    try:
        result = mimasa_instance.translate()
        async_process.update_state(state="SUCCESS", meta={"result": result})
    except Exception as e:
        mimasa_instance.task_status = "FAILURE"
        mimasa_instance.save()
        async_process.update_state(state="FAILURE", meta={"exc_type": type(e).__name__, "exc_message": str(e)})
        raise
