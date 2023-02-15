import os
import shutil

from django.test import TestCase, Client
from rest_framework import status
from django.urls import reverse
from django.conf import settings
from src.common.libraries import Config
from channels.testing import WebsocketCommunicator
from .consumers import AudioSeparationConsumer


class AudioSeparationCreateViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = "/api/audio_separation/"
        self.media_root = settings.MEDIA_ROOT
        self.audio_separation_base = os.path.join(self.media_root, "tmp", "audio_separation")
        if not os.path.exists(self.audio_separation_base):
            os.makedirs(self.audio_separation_base)

    def tearDown(self):
        shutil.rmtree(self.audio_separation_base)

    def test_run_synchronously_valid_data(self):
        audio_filepath = Config.AUDIO_INPUT_FILENAME

        # Prepare the data for the request
        data = {"audio_filepath": audio_filepath, "destination_folder": self.audio_separation_base}

        # Send the post request
        response = self.client.post(self.url, data, format="multipart")

        # Check the response status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if the response contains the expected data
        music_file = os.path.join(self.audio_separation_base, response.data["music_filename"])
        speech_file = os.path.join(self.audio_separation_base, response.data["speech_filename"])

        self.assertTrue(os.path.exists(music_file))
        self.assertTrue(os.path.exists(speech_file))

    def test_audio_file_does_not_exist(self):
        # Prepare the data for the request
        data = {"audio_filepath": "invalid_filepath", "destination_folder": self.audio_separation_base}

        # Send the post request
        response = self.client.post(self.url, data, format="json")

        # Check the response status code
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Check if the response contains the error message
        self.assertEqual(response.data["error"], "Audio file not found")

    def test_destination_folder_does_not_exist(self):
        audio_filepath = Config.AUDIO_INPUT_FILENAME

        # Prepare the data for the request
        data = {"audio_filepath": audio_filepath, "destination_folder": "invalid_destination_folder"}

        # Send the post request
        response = self.client.post(self.url, data, format="json")

        # Check the response status code
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Check if the response contains the error message
        self.assertEqual(response.data["error"], "Destination folder not found")

    def test_run_in_background(self):
        audio_filepath = Config.AUDIO_INPUT_FILENAME
        data = {
            "audio_filepath": audio_filepath,
            "destination_folder": self.audio_separation_base,
            "run_in_background": True,
        }
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertIn("task_id", response.data)
        self.assertEqual(response.data["message"], "audio separation request received")


from unittest.mock import MagicMock, patch
from rest_framework.test import APITestCase
from django.core.cache import cache
from .serializers import TaskIdSerializer
from .views import AudioSeparationRetrieveView


class AudioSeparationRetrieveViewTestCase(APITestCase):
    def setUp(self):
        self.url = reverse("audio_separation_results", kwargs={"task_id": "test_task_id"})
        self.task_id = "test_task_id"
        self.data = {"task_id": self.task_id}
        self.serializer = TaskIdSerializer(data=self.data)
        self.request = MagicMock()
        self.view = AudioSeparationRetrieveView()
        self.request.data = self.data

    @patch("django.core.cache.cache.set")
    def test_pending_task(self, mock_cache_set):
        task_result = MagicMock(name="AsyncResult")
        task_result.state = "PENDING"
        mock_cache_set.side_effect = lambda key, value, timeout=None: None

        response = self.view.get(self.request, task_id=self.task_id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"type": "pending"})

    @patch("django.core.cache.cache.set")
    def test_successful_task(self, mock_cache_set):
        task_result = MagicMock(name="AsyncResult")
        task_result.state = "SUCCESS"
        task_result.result = {"music_filename": "test_music.mp3", "speech_filename": "test_speech.wav"}
        mock_cache_set.side_effect = lambda key, value, timeout=None: None

        with patch("audio_separation.views.AsyncResult", return_value=task_result):
            response = self.view.get(self.request, task_id=self.task_id)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.data,
                {"type": "success", "music_filename": "test_music.mp3", "speech_filename": "test_speech.wav"},
            )

    @patch("django.core.cache.cache.set")
    def test_failed_task(self, mock_cache_set):
        task_result = MagicMock(name="AsyncResult")
        task_result.state = "FAILURE"
        task_result.result = {"exc_type": "ValueError", "exc_message": "Test error"}
        mock_cache_set.side_effect = lambda key, value, timeout=None: None

        with patch("audio_separation.views.AsyncResult", return_value=task_result):
            response = self.view.get(self.request, task_id=self.task_id)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data, {"type": "error", "exc_type": "ValueError", "exc_message": "Test error"})

    @patch("django.core.cache.cache.set")
    def test_unknown_task(self, mock_cache_set):
        task_result = MagicMock(name="AsyncResult")
        task_result.state = "UNKNOWN"
        mock_cache_set.side_effect = lambda key, value, timeout=None: None

        with patch("audio_separation.views.AsyncResult", return_value=task_result):
            response = self.view.get(self.request, task_id=self.task_id)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data, {"type": "unknown", "message": "This should never be reached"})


# class TestAudioSeparationRetrieveConsumer(TestCase):
#     async def test_consumer(self):
#         communicator = WebsocketCommunicator(AudioSeparationConsumer.as_asgi(), "/test/")

#         connected, _ = await communicator.connect()
#         self.assertTrue(connected)

#         task_result = ("path/to/music_file.mp3", "path/to/speech_file.mp3", "SUCCESS")
#         self.task.result = lambda: task_result
#         self.task.status = "SUCCESS"

#         await communicator.receive_json_from()
#         response = await communicator.receive_json_from()

#         self.assertEqual(
#             response,
#             {
#                 "music_filename": "path/to/music_file.mp3",
#                 "speech_filename": "path/to/speech_file.mp3",
#                 "status": "SUCCESS",
#             },
#         )

#         await communicator.disconnect()

# class AudioSeparationConsumerTestCase(TestCase):
#     async def test_successful_task(self):
#         task_id = "test_task_id"
#         task_result = MagicMock(name="AsyncResult")
#         task_result.ready.return_value = True
#         task_result.state = "SUCCESS"
#         task_result.result = {"music_filename": "test_music_file", "speech_filename": "test_speech_file"}

#         with patch("celery.result.AsyncResult", return_value=task_result):
#             communicator = WebsocketCommunicator(AudioSeparationConsumer.as_asgi(), f"/ws/audio_separation/{task_id}/")
#             connected, _ = await communicator.connect()
#             self.assertTrue(connected)

#             message = await communicator.receive_json_from()
#             self.assertEqual(message["type"], "success")
#             self.assertEqual(message["music_filename"], "test_music_file")
#             self.assertEqual(message["speech_filename"], "test_speech_file")

#             await communicator.disconnect()

#     async def test_failed_task(self):
#         task_id = "test_task_id"
#         task_result = MagicMock(name="AsyncResult")
#         task_result.ready.return_value = True
#         task_result.state = "FAILURE"
#         task_result.result = {"exc_type": "ValueError", "exc_message": "Test error"}

#         with patch("celery.result.AsyncResult", return_value=task_result):
#             communicator = WebsocketCommunicator(AudioSeparationConsumer.as_asgi(), f"/ws/audio_separation/{task_id}/")
#             connected, _ = await communicator.connect()
#             self.assertTrue(connected)

#             message = await communicator.receive_json_from()
#             self.assertEqual(message["type"], "error")
#             self.assertEqual(message["exc_type"], "ValueError")
#             self.assertEqual(message["exc_message"], "Test error")

#             await communicator.disconnect()
