import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mimasa.settings")

app = Celery("mimasa")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
