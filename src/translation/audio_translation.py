#!/usr/bin/env python3
"""
AudioTranslation class is the main entry point for the audio related processing.
"""
from src.audioseparator import utils as separator_utils
from src.common.libraries import Audio, Config, Logger


class AudioTranslation:
    """Class for translating audio in a file"""

    def __init__(self, audio: Audio, output_language: str, input_language: str = "unknown"):
        """
        Initialize an AudioTranslation object with an audio object

        :param audio: a valid audio object
        """
        self.audio = audio
        self.output_language = output_language
        self.input_language = input_language
        self.audio_file = audio.get_filename()
        self.audio_separator = None

        self.logger = Logger(self.__class__.__name__)
        self.logger.add_file_handler("audio_translation.log")

        self._initialize()

    def _initialize(self):
        self.logger.debug("Initializing audio translation unit...")
        self.audio_separator = separator_utils.get_audio_separator(Config.AUDIO_SEPARATOR)
        self.logger.debug("Audio translation unit is initialized successfully")

    async def translate(self):
        """Asynchronous coroutine for performing the audio translation"""
        self.logger.debug(f"Starting audio translation for file: {self.audio_file}")
        try:
            await self.audio_separator.separate_vocals_and_music(
                audio=self.audio, destination=f"{Config.TRANSLATION_OUTPUT_PATH}"
            )
            self.logger.info(f"Audio translation completed successfully for file: {self.audio_file}")
        except Exception as e:
            self.logger.error(f"Error during audio translation for file: {self.audio_file}: {e}")
