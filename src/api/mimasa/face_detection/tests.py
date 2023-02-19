import os
import shutil

from pathlib import Path
from unittest.mock import MagicMock, patch
from django.conf import settings
from django.test import TestCase
from rest_framework import status

from .serializers import FaceDetectionSerializer, TaskIdSerializer
from .views import FaceDetectionCreateView, FaceDetectionRetrieveView
from src.common.libraries import Config


class FaceDetectionCreateViewTest(TestCase):
    def setUp(self):
        self.view = FaceDetectionCreateView.as_view()
        self.media_root = settings.MEDIA_ROOT
        self.face_detection_base = os.path.join(self.media_root, "tmp", "face_detection")
        if not os.path.exists(self.face_detection_base):
            os.makedirs(self.face_detection_base)
        self.valid_payload = {
            "video_filepath": Path(Config.TRANSLATION_INPUT_PATH / "movie4.mp4"),
            "destination_folder": self.face_detection_base,
            "run_in_background": False,
            "async_enabled": True,
            "async_type": "ConcurrentFuturesFaceDetector",
            "detector_type": "MTCNN",
        }

    def tearDown(self):
        shutil.rmtree(self.face_detection_base)

    def test_valid_payload(self):
        # Mock the serializer and face_detection_service
        serializer_mock = MagicMock(spec=FaceDetectionSerializer)
        serializer_mock.is_valid.return_value = True
        serializer_mock.validated_data = self.valid_payload
        with patch("face_detection.views.FaceDetectionSerializer", return_value=serializer_mock):
            with patch("face_detection.views.face_detection_service", return_value={"message": "Success"}):
                response = self.client.post("/api/face_detection/", data=self.valid_payload)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(response.data, {"message": "Success"})

    def test_invalid_payload(self):
        # Mock the serializer
        serializer_mock = MagicMock(spec=FaceDetectionSerializer)
        serializer_mock.is_valid.return_value = False
        serializer_mock.errors = {"destination_folder": ["This field is required."]}
        with patch("face_detection.views.FaceDetectionSerializer", return_value=serializer_mock):
            response = self.client.post("/api/face_detection/", data={})
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_video_file_not_found(self):
        # Mock the serializer
        serializer_mock = MagicMock(spec=FaceDetectionSerializer)
        serializer_mock.is_valid.return_value = True
        serializer_mock.validated_data = self.valid_payload
        with patch("face_detection.views.FaceDetectionSerializer", return_value=serializer_mock):
            with patch("os.path.exists", return_value=False):
                response = self.client.post("/api/face_detection/", data=self.valid_payload)
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertEqual(response.data, {"error": "Video file not found"})

    def test_destination_folder_not_found(self):
        # Mock the serializer
        serializer_mock = MagicMock(spec=FaceDetectionSerializer)
        serializer_mock.is_valid.return_value = True
        serializer_mock.validated_data = self.valid_payload
        with patch("face_detection.views.FaceDetectionSerializer", return_value=serializer_mock):
            with patch("os.path.exists", side_effect=[True, False]):
                response = self.client.post("/api/face_detection/", data=self.valid_payload)
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertEqual(response.data, {"error": "Destination folder not found"})

    def test_run_in_background(self):
        # Mock the serializer and run_face_detection task
        serializer_mock = MagicMock(spec=FaceDetectionSerializer)
        serializer_mock.is_valid.return_value = True
        serializer_mock.validated_data = self.valid_payload
        self.valid_payload["run_in_background"] = True
        self.valid_payload["async_type"] = "AsyncTaskFaceDetector"
        with patch("face_detection.views.FaceDetectionSerializer", return_value=serializer_mock):
            with patch("face_detection.views.run_face_detection.delay") as run_face_detection_mock:
                task_mock = MagicMock()
                task_mock.id = "test_task_id"
                run_face_detection_mock.return_value = task_mock

                response = self.client.post("/api/face_detection/", data=self.valid_payload)

                # Assert that the response is correct
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(
                    response.data, {"task_id": "test_task_id", "message": "face detection request received"}
                )

                # Assert that the run_face_detection task is called with the correct arguments
                run_face_detection_mock.assert_called_once_with(
                    str(self.valid_payload["video_filepath"]),
                    self.valid_payload["destination_folder"],
                    self.valid_payload["async_enabled"],
                    self.valid_payload["async_type"],
                    self.valid_payload["detector_type"],
                )

    def test_invalid_async_type(self):
        # Mock the serializer
        invalid_payload = self.valid_payload.copy()
        invalid_payload["async_enabled"] = True
        invalid_payload["async_type"] = "InvalidAsyncType"
        serializer_mock = MagicMock(spec=FaceDetectionSerializer)
        serializer_mock.is_valid.return_value = True
        serializer_mock.validated_data = invalid_payload
        with patch("face_detection.views.FaceDetectionSerializer", return_value=serializer_mock):
            response = self.client.post("/api/face_detection/", data=invalid_payload)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                response.data,
                {"async_type": ['"InvalidAsyncType" is not a valid choice.']},
            )

    def test_invalid_detector_type(self):
        # Mock the serializer
        invalid_payload = self.valid_payload.copy()
        invalid_payload["detector_type"] = "InvalidDetectorType"
        serializer_mock = MagicMock(spec=FaceDetectionSerializer)
        serializer_mock.is_valid.return_value = True
        serializer_mock.validated_data = invalid_payload
        with patch("face_detection.views.FaceDetectionSerializer", return_value=serializer_mock):
            response = self.client.post("/api/face_detection/", data=invalid_payload)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                response.data,
                {"detector_type": ['"InvalidDetectorType" is not a valid choice.']},
            )


from django.urls import reverse
from django.test import TestCase, Client
from rest_framework import status
from unittest.mock import patch
from celery.result import AsyncResult


class FaceDetectionRetrieveViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("face_detection_results", kwargs={"task_id": "test-task-id"})
        self.task_result = MagicMock(name="AsyncResult")

    @patch("face_detection.views.AsyncResult")
    def test_successful_retrieval(self, AsyncResultMock):
        AsyncResultMock.return_value = self.task_result
        self.task_result.state = "SUCCESS"
        self.task_result.result = {"video_filename": "test.mp4"}

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "type": "success",
                "video_filename": "test.mp4",
            },
        )

    @patch("face_detection.views.AsyncResult")
    def test_pending_retrieval(self, AsyncResultMock):
        AsyncResultMock.return_value = self.task_result
        self.task_result.state = "PENDING"

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "type": "pending",
            },
        )

    @patch("face_detection.views.AsyncResult")
    def test_failure_retrieval(self, AsyncResultMock):
        AsyncResultMock.return_value = self.task_result
        self.task_result.state = "FAILURE"
        self.task_result.result = {
            "exc_type": "ValueError",
            "exc_message": "Invalid input",
        }

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "type": "error",
                "exc_type": "ValueError",
                "exc_message": "Invalid input",
            },
        )

    @patch("face_detection.views.AsyncResult")
    def test_unknown_retrieval(self, AsyncResultMock):
        AsyncResultMock.return_value = self.task_result
        self.task_result.state = "UNKNOWN"

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "type": "unknown",
                "message": "This should never be reached",
            },
        )
