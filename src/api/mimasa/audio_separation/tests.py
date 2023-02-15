import os
import shutil

from django.test import TestCase, Client
from rest_framework import status
from django.urls import reverse
from .models import AudioSeparationModel
from django.conf import settings
from src.common.libraries import Config


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


class AudioSeparationRetrieveViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.separator = AudioSeparationModel.objects.create(
            music_filename="music.mp3", speech_filename="speech.mp3", task_status="SUCCESS"
        )

    def test_retrieve_valid_audio_separation(self):
        response = self.client.get(reverse("audio_separation_results", kwargs={"pk": self.separator.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["music_filename"], "music.mp3")
        self.assertEqual(response.data["speech_filename"], "speech.mp3")
        self.assertEqual(response.data["status"], "SUCCESS")

    def test_retrieve_invalid_audio_separation(self):
        response = self.client.get(reverse("audio_separation_results", kwargs={"pk": 0}))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, {"error": "Audio separation task not found"})


import unittest
from channels.testing import WebsocketCommunicator
from .consumers import AudioSeparationConsumer


class TestAudioSeparationRetrieveConsumer(unittest.TestCase):
    async def test_consumer(self):
        communicator = WebsocketCommunicator(AudioSeparationConsumer.as_asgi(), "/test/")

        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        task_result = ("path/to/music_file.mp3", "path/to/speech_file.mp3", "SUCCESS")
        self.task.result = lambda: task_result
        self.task.status = "SUCCESS"

        await communicator.receive_json_from()
        response = await communicator.receive_json_from()

        self.assertEqual(
            response,
            {
                "music_filename": "path/to/music_file.mp3",
                "speech_filename": "path/to/speech_file.mp3",
                "status": "SUCCESS",
            },
        )

        await communicator.disconnect()
