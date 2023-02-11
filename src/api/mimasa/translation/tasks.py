from .models import  MimasaModel
from mimasa.celery import app

@app.task
def async_process(pk):
    try:
        print(f'Processing {pk}...')
        mimasa_instance = MimasaModel.objects.get(id=pk)
        mimasa_instance.translate()
    except Exception as e:
        async_process.update_state(state='FAILURE', meta={'exc_type': type(e).__name__, 'exc_message': str(e)})
        raise
