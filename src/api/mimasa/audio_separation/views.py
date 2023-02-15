import os

from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from .serializers import AudioSeparationSerializer, TaskIdSerializer
from .models import AudioSeparationModel
from .services import audio_separation_service
from .tasks import run_audio_separation
from celery.result import AsyncResult


class AudioSeparationCreateView(generics.CreateAPIView):
    serializer_class = AudioSeparationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            audio_filepath = serializer.validated_data.get("audio_filepath")
            destination_folder = serializer.validated_data.get("destination_folder")
            run_in_background = serializer.validated_data.get("run_in_background")

            # check if the audio file exists
            if not os.path.exists(audio_filepath):
                return Response({"error": "Audio file not found"}, status=status.HTTP_400_BAD_REQUEST)

            # check if the destination folder exists
            if not os.path.exists(destination_folder):
                return Response({"error": "Destination folder not found"}, status=status.HTTP_400_BAD_REQUEST)

            if run_in_background:
                # run the audio_separation task in the background
                task = run_audio_separation.delay(audio_filepath, destination_folder)
                return Response({"task_id": task.id, "message": "audio separation request received"})
            else:
                result = audio_separation_service(audio_filepath=audio_filepath, destination=destination_folder)
                return Response(result)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# TODO: can be removed or modfied to check status based on given task_id
class AudioSeparationRetrieveView(generics.RetrieveAPIView):
    serializer_class = TaskIdSerializer

    def get(self, request, *args, **kwargs):
        try:
            print(kwargs.get("id"))
            separator = AudioSeparationModel.objects.get(id=kwargs.get("pk"))
        except AudioSeparationModel.DoesNotExist:
            return Response({"error": "Audio separation task not found"}, status=status.HTTP_404_NOT_FOUND)

        result = AsyncResult(separator.task_id)
        meta = result.result or result.state
        if separator.task_status == "SUCCESS":
            return Response(
                {
                    "status": separator.task_status,
                    "music_filename": separator.music_filename,
                    "speech_filename": separator.speech_filename,
                    "meta": meta,
                }
            )
        elif separator.task_status == "FAILURE":
            return Response(
                {
                    "status": separator.task_status,
                    "music_filename": separator.music_filename,
                    "speech_filename": separator.speech_filename,
                    "meta": meta,
                }
            )
        else:
            return Response({"status": separator.task_status})
