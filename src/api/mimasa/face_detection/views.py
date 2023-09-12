import os

from celery.result import AsyncResult
from rest_framework import generics, status
from rest_framework.response import Response

from .serializers import FaceDetectionSerializer, TaskIdSerializer
from .services import face_detection_service
from .tasks import run_face_detection


class FaceDetectionCreateView(generics.CreateAPIView):
    serializer_class = FaceDetectionSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            video_filepath = serializer.validated_data.get("video_filepath")
            destination_folder = serializer.validated_data.get("destination_folder")
            run_in_background = serializer.validated_data.get("run_in_background")
            async_enabled = serializer.validated_data.get("async_enabled")
            async_type = serializer.validated_data.get("async_type")
            detector_type = serializer.validated_data.get("detector_type")

            # check if the audio file exists
            if not os.path.exists(video_filepath):
                return Response({"error": "Video file not found"}, status=status.HTTP_400_BAD_REQUEST)

            # check if the destination folder exists
            if not os.path.exists(destination_folder):
                return Response({"error": "Destination folder not found"}, status=status.HTTP_400_BAD_REQUEST)

            if run_in_background:
                # run the face_detection task in the background
                task = run_face_detection.delay(
                    video_filepath, destination_folder, async_enabled, async_type, detector_type
                )
                return Response({"task_id": task.id, "message": "face detection request received"})
            else:
                result = face_detection_service(
                    video_filepath=video_filepath,
                    destination=destination_folder,
                    async_enabled=async_enabled,
                    async_type=async_type,
                    detector_type=detector_type,
                )
                return Response(result)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FaceDetectionRetrieveView(generics.RetrieveAPIView):
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
                    "video_filename": result["video_filename"],
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
