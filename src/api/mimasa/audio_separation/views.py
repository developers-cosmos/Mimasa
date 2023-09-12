import os

from celery.result import AsyncResult
from rest_framework import generics, status
from rest_framework.response import Response

from .serializers import AudioSeparationSerializer, TaskIdSerializer
from .services import audio_separation_service
from .tasks import run_audio_separation


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


class AudioSeparationRetrieveView(generics.RetrieveAPIView):
    serializer_class = TaskIdSerializer

    def get(self, request, *args, **kwargs):
        task_id = kwargs.get("task_id")
        task_result = AsyncResult(task_id)

        if task_result.state == "PENDING":
            return Response({"type": "pending"})

        result = task_result.result
        if task_result.state == "SUCCESS":
            return Response(
                {
                    "type": "success",
                    "music_filename": result["music_filename"],
                    "speech_filename": result["speech_filename"],
                }
            )
        elif task_result.state == "FAILURE":
            return Response(
                {
                    "type": "error",
                    "exc_type": result["exc_type"],
                    "exc_message": result["exc_message"],
                }
            )
        else:
            return Response({"type": "unknown", "message": "This should never be reached"})
