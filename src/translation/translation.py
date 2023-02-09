#!/usr/bin/env python3
"""
Translation class is the main entry point for the application, and it creates two
separate asynchronous tasks for the audio and video translations.
"""
import asyncio

from src.common.libraries import Logger, Video, Audio, Config
from src.translation.audio_extractor import AudioExtractor
from src.translation.video_translation import VideoTranslation
from src.translation.audio_translation import AudioTranslation
from src.utils import utils


class Translation:
    """Class for extracting audio from a video file and performing audio and video translations in parallel"""

    def __init__(self, video: Video, output_language: str, input_language: str = "Unknown"):
        """
        Initialize a Translation object with a video file

        :param video: a valid video object
        """
        self.video = video
        self.output_language = output_language
        self.input_language = input_language

        self.video_file = video.get_filename()
        self.extracted_audio_file = f"{Config.TRANSLATION_OUTPUT_PATH}/extracted_audio_{utils.get_filename_from_path(self.video_file).split('.')[0]}.wav"
        self.extracted_audio = Audio(file_path=self.extracted_audio_file, language=self.input_language)

        self.logger = Logger(self.__class__.__name__)
        self.logger.add_file_handler("translation.log")

        self._initialize()

    def _initialize(self):
        self.logger.debug("Initializing translation unit...")
        self.audio_extractor = AudioExtractor(video=self.video)
        self.audio_translation = AudioTranslation(
            audio=self.extracted_audio, output_language=self.output_language, input_language=self.input_language
        )
        self.video_translation = VideoTranslation(self.video)
        self.logger.debug("Translation unit initialized successfully")

    async def translate_audio(self):
        """Asynchronous coroutine for performing the audio translation"""
        self.logger.debug("Starting audio translation")
        try:
            await self.audio_translation.translate()
            self.logger.info("Audio translation completed successfully")
        except Exception as e:
            self.logger.error(f"Error during audio translation: {e}")

    async def translate_video(self):
        """Asynchronous coroutine for performing the video translation"""
        self.logger.debug("Starting video translation")
        try:
            await self.video_translation.translate()
            self.logger.info("Video translation completed successfully")
        except Exception as e:
            self.logger.error(f"Error during video translation: {e}")

    async def translate(self):
        """Asynchronous coroutine for performing both audio and video translations in parallel"""
        self.logger.debug("Starting parallel audio and video translations")
        try:
            self.audio_extractor.extract(output_file=self.extracted_audio_file)
            translation_tasks = [
                self.translate_audio(),
                self.translate_video(),
            ]
            await asyncio.gather(*translation_tasks)
            self.logger.info("Parallel audio and video translations completed successfully")
        except Exception as e:
            self.logger.critical(f"Error during parallel audio and video translations: {e}")
            raise
