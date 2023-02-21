import os
import shutil

from pathlib import Path
from unittest.mock import MagicMock, patch
from django.conf import settings
from django.test import TestCase
from rest_framework import status
from rest_framework import serializers

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
            "async_type": "AsyncTaskFaceDetector",
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

    def test_invalid_data_detector_type_not_implemented(self):
        invalid_data_detector_type_not_implemented = {
            "video_filepath": "some/dummy/video_file.mp4",
            "destination_folder": "some/dummy/destination_folder",
            "detector_type": "YOLO",
        }
        serializer_mock = MagicMock(spec=FaceDetectionSerializer)
        serializer_mock.is_valid.return_value = True
        serializer_mock.validated_data = invalid_data_detector_type_not_implemented
        with patch("face_detection.views.FaceDetectionSerializer", return_value=serializer_mock):
            response = self.client.post("/api/face_detection/", data=invalid_data_detector_type_not_implemented)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                response.json(),
                {"non_field_errors": ["The selected face detector is not implemented."]},
            )

    def test_invalid_data_async_type_not_supported(self):
        invalid_data_async_type_not_supported = {
            "video_filepath": "some/dummy/video_file.mp4",
            "destination_folder": "some/dummy/destination_folder",
            "run_in_background": True,
            "async_type": "ConcurrentFuturesFaceDetector",
        }
        serializer_mock = MagicMock(spec=FaceDetectionSerializer)
        serializer_mock.is_valid.return_value = True
        serializer_mock.validated_data = invalid_data_async_type_not_supported
        with patch("face_detection.views.FaceDetectionSerializer", return_value=serializer_mock):
            response = self.client.post("/api/face_detection/", data=invalid_data_async_type_not_supported)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                response.json(),
                {"non_field_errors": ["The selected async_type is currently not supported to run in background."]},
            )


from django.test import TestCase
from rest_framework import serializers


class TaskIdSerializerTestCase(TestCase):
    def setUp(self):
        self.serializer = TaskIdSerializer()

    def test_valid_data(self):
        data = {"task_id": "65a9c1eb-451c-4c3d-b970-d7410016e1ad"}
        result = self.serializer.validate(data)
        self.assertEqual(result, data)

    # TODO: Implement custom validate_task_id() in TaskIdSerializer() if needed
    # def test_missing_field(self):
    #     data = {}
    #     result = self.serializer.validate(data)
    #     self.assertEqual(
    #         result,
    #         {"task_id": ["This field is required."]}
    #     )

    # def test_invalid_data(self):
    #     data = {"task_id": 123}
    #     result = self.serializer.validate(data)
    #     self.assertEqual(
    #         result,
    #         {"task_id": ["Expected a string."]}
    #     )


from django.urls import reverse
from django.test import TestCase, Client
from rest_framework import status
from unittest.mock import patch


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


from unittest.mock import patch, MagicMock
from unittest import IsolatedAsyncioTestCase
from channels.testing import WebsocketCommunicator
from .consumers import FaceDetectionConsumer
from mimasa.asgi import application


class FaceDetectionConsumerTestCase(IsolatedAsyncioTestCase):
    def setUp(self):
        self.task_id = "some-task-id"
        self.result = {"video_filename": "some-video-filename.mp4"}

        self.consumer = FaceDetectionConsumer()
        self.communicator = WebsocketCommunicator(application, f"/ws/face_detection/{self.task_id}/")

    async def test_successful_detection(self):
        with patch("face_detection.consumers.AsyncResult") as mock_result:
            mock_task = MagicMock()
            mock_task.ready.return_value = True
            mock_task.state = "SUCCESS"
            mock_task.result = self.result
            mock_result.return_value = mock_task

            connected, _ = await self.communicator.connect()
            self.assertTrue(connected)

            response = await self.communicator.receive_json_from()

            await self.communicator.disconnect()

        self.assertEqual(response["type"], "success")
        self.assertEqual(response["video_filename"], self.result["video_filename"])

    async def test_failed_detection(self):
        with patch("face_detection.consumers.AsyncResult") as mock_result:
            mock_task = MagicMock()
            mock_task.ready.return_value = True
            mock_task.state = "FAILURE"
            mock_task.result = {"exc_type": "ValueError", "exc_message": "Invalid input"}
            mock_result.return_value = mock_task

            connected, _ = await self.communicator.connect()
            self.assertTrue(connected)

            response = await self.communicator.receive_json_from()

            await self.communicator.disconnect()

        self.assertEqual(response["type"], "error")
        self.assertEqual(response["exc_type"], mock_task.result["exc_type"])
        self.assertEqual(response["exc_message"], mock_task.result["exc_message"])
