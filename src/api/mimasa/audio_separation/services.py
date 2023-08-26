import os
import asyncio
from src.audioseparator import utils
from src.common.libraries import Audio, Config


def audio_separation_service(audio_filepath: str, destination: str):
    try:
        audio = Audio(audio_filepath)
        audio_separator = utils.get_audio_separator(Config.AUDIO_SEPARATOR)
        music_filepath, speech_filepath = asyncio.run(
            audio_separator.separate_vocals_and_music(audio=audio, destination=destination)
        )
        return {
            "music_filename": os.path.basename(music_filepath),
            "speech_filename": os.path.basename(speech_filepath),
        }
    except Exception as e:
        return {
            "error": str(e),
            "exc_type": type(e).__name__,
        }


# from nameko.rpc import rpc

# class AudioSeparationService:
#     name = "audio_separation_service"

#     @rpc
#     def separate_vocals_and_music(self, audio_filepath: str, destination: str):
#         audio_separation_service(audio_filepath=audio_filepath, destination=destination)
