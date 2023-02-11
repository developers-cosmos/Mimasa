from .models import MimasaModel
from mimasa.celery import app


@app.task
def run_translation(pk):
    print(f"Processing {pk}...")
    mimasa_instance = MimasaModel.objects.get(id=pk)
    try:
        result = mimasa_instance.translate()
        run_translation.update_state(state="SUCCESS", meta={"result": result})
    except Exception as e:
        mimasa_instance.task_status = "FAILURE"
        mimasa_instance.save()
        run_translation.update_state(state="FAILURE", meta={"exc_type": type(e).__name__, "exc_message": str(e)})
        raise
