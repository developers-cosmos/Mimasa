from django.db import models


## NOTE: This model is no longer used

# class AudioSeparationModel(models.Model):
#     TASK_STATUS = (
#         ("pending", "PENDING"),
#         ("processing", "PROCESSING"),
#         ("success", "SUCCESS"),
#         ("failure", "FAILURE"),
#     )

#     id = models.AutoField(primary_key=True)
#     task_id = models.CharField(max_length=100, unique=True)
#     audio_filepath = models.CharField(max_length=500)
#     destination_folder = models.CharField(max_length=500)
#     task_status = models.CharField(max_length=100, default="PENDING")
#     created_at = models.DateTimeField(auto_now_add=True)
#     music_filename = models.CharField(max_length=100, blank=True, null=True)
#     speech_filename = models.CharField(max_length=100, blank=True, null=True)
