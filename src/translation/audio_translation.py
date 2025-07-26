#!/usr/bin/env python3
"""
High-level audio translation for Mimasa.

This class currently performs vocal/music separation using the configured
audio separator and then returns the path to the isolated vocals file.  It
provides a hook where future implementations can perform speech-to-text,
machine translation and text-to-speech synthesis.  The original code in
``src/translation/audio_translation.py`` did not return a value from the
``translate`` coroutine, which prevented the pipeline from obtaining the
location of the translated audio.  This refactored version fixes that and
stores the translated audio path on the instance as ``translated_audio_file``.
"""

from typing import Optional, Tuple

from src.audioseparator import utils as separator_utils
from src.common.libraries import Audio, Config, Logger


class AudioTranslation:
    """Class for translating audio in a file."""

    def __init__(self, audio: Audio, output_language: str, input_language: str = "unknown"):
        self.audio = audio
        self.output_language = output_language
        self.input_language = input_language
        self.audio_file = audio.get_filename()
        self.audio_separator = None
        self.translated_audio_file: Optional[str] = None

        self.logger = Logger(self.__class__.__name__)
        self.logger.add_file_handler("audio_translation.log")

        self._initialize()

    def _initialize(self) -> None:
        self.logger.debug("Initializing audio translation unit...")
        self.audio_separator = separator_utils.get_audio_separator(Config.AUDIO_SEPARATOR)
        self.logger.debug("Audio translation unit is initialized successfully")

    async def translate(self) -> Optional[str]:
        """
        Asynchronous coroutine for performing the audio translation.

        Returns the path to the translated audio (currently the isolated vocals).
        Downstream consumers should check for ``None`` and fall back to the
        extracted audio if necessary.
        """
        self.logger.debug(f"Starting audio translation for file: {self.audio_file}")
        try:
            # Separate vocals and music; use the vocals as the translated audio
            music_path, vocals_path = await self.audio_separator.separate_vocals_and_music(
                audio=self.audio,
                destination=f"{Config.TRANSLATION_OUTPUT_PATH}"
            )
            self.logger.info(
                f"Audio translation completed successfully for file: {self.audio_file}."
            )
            # In a future implementation you would perform speech-to-text,
            # translation and text-to-speech here.  For now return the vocals.
            self.translated_audio_file = vocals_path
            return self.translated_audio_file
        except Exception as e:
            self.logger.error(f"Error during audio translation for file: {self.audio_file}: {e}")
            return None
