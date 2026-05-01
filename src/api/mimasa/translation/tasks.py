from mimasa.celery import app

from .models import MimasaModel, TranslationNotification


@app.task(bind=True)
def run_translation(self, pk):
    mimasa_instance = MimasaModel.objects.get(id=pk)
    mimasa_instance.task_status = "PENDING"
    mimasa_instance.task_id = self.request.id or "unknown"
    mimasa_instance.save(update_fields=["task_status", "task_id", "updated_at"])

    try:
        output_video = mimasa_instance.translate()
        mimasa_instance.task_status = "SUCCESS"
        mimasa_instance.save(update_fields=["task_status", "updated_at"])

        token = TranslationNotification.generate_token()
        TranslationNotification.objects.create(
            user=mimasa_instance.user,
            translation=mimasa_instance,
            message="Your translation is ready to download.",
            download_token=token,
        )

        self.update_state(state="SUCCESS", meta={"result": output_video, "download_token": token})
        return {"result": output_video, "download_token": token}
    except Exception as exc:
        mimasa_instance.task_status = "FAILURE"
        mimasa_instance.save(update_fields=["task_status", "updated_at"])
        TranslationNotification.objects.create(
            user=mimasa_instance.user,
            translation=mimasa_instance,
            message="Translation failed. Please retry your request.",
        )
        self.update_state(state="FAILURE", meta={"exc_type": type(exc).__name__, "exc_message": str(exc)})
        raise
