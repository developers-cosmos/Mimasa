import os

from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from .serializers import AudioSeparationSerializer, TaskIdSerializer
from .models import AudioSeparationModel
from .services import audio_separation_service
from .tasks import run_audio_separation
from src.common.audio import Audio
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
                # Save task information in the database
                separation_model = AudioSeparationModel(
                    audio_filepath=audio_filepath, destination_folder=destination_folder
                )
                separation_model.save()

                # run the audio_separation task in the background
                task_result = run_audio_separation.delay(separation_model.id)
                separation_model.task_status = task_result.status
                separation_model.task_id = task_result.task_id
                separation_model.save()

                return Response(
                    {"separation_request_id": separation_model.id, "message": "audio separation request received"}
                )
            else:
                audio_obj = Audio(file_path=audio_filepath)
                result = audio_separation_service(audio=audio_obj, destination=destination_folder)
                if isinstance(result, Response):
                    return result
                else:
                    music_filename, speech_filename = result
                    return Response({"music_filename": music_filename, "speech_filename": speech_filename})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
