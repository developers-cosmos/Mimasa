import os
import asyncio
from rest_framework.response import Response
from rest_framework import status
from src.audioseparator import utils
from src.common.libraries import Audio, Config


def audio_separation_service(audio: Audio, destination: str):
    try:
        audio_separator = utils.get_audio_separator(Config.AUDIO_SEPARATOR)
        music_filepath, speech_filepath = asyncio.run(
            audio_separator.separate_vocals_and_music(audio=audio, destination=destination)
        )
        return os.path.basename(music_filepath), os.path.basename(speech_filepath)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
