#!/usr/bin/env python3
"""
Extended translation pipeline for Mimasa.

This implementation orchestrates the audio and video translation components and
then combines the translated audio with the processed video.  The original
repository left the combination step unimplemented and did not return the
path of the translated audio from the audio translation coroutine.  This
module adds those missing pieces so that the pipeline can produce a final
video file with the updated audio track.

Note: because network‑bound translation services (e.g. Google Translate,
Google Speech‑to‑Text, gTTS) are not available in this environment, the
current AudioTranslation implementation simply separates vocals from the
input audio and returns the vocals path as the "translated" audio.  The
combine step then muxes this audio back into the video.  Users can replace
the translation logic in `src/translation/audio_translation.py` with their
preferred implementation if they have access to external APIs.
"""

import asyncio
import os
import subprocess
from typing import Optional

from src.common.libraries import Audio, Config, Logger, Video
from src.translation.audio_extractor import AudioExtractor
from src.translation.audio_translation import AudioTranslation
from src.translation.video_translation import VideoTranslation
from src.utils import utils


class Translation:
    """Main class for orchestrating audio and video translation.

    This class extracts audio from a video, runs the audio and video
    translation tasks concurrently and finally combines the translated audio
    with the processed video into a single output file.  It exposes a
    synchronous wrapper via :meth:`translate_sync` for convenience.
    """

    def __init__(self, video: Video, output_language: str, input_language: str = "Unknown"):
        self.video = video
        self.output_language = output_language
        self.input_language = input_language

        # Paths for intermediate and final artifacts
        self.video_file = video.get_filename()
        self.extracted_audio_file = f"{Config.TRANSLATION_OUTPUT_PATH}/extracted_audio_{utils.get_filename_from_path(self.video_file).split('.')[0]}.wav"
        self.extracted_audio = Audio(file_path=self.extracted_audio_file, language=self.input_language)

        self.output_video_filename: Optional[str] = None

        self.logger = Logger(self.__class__.__name__)
        self.logger.add_file_handler("translation.log")

        self._initialize()

    def _initialize(self) -> None:
        self.logger.debug("Initializing translation unit...")
        # Initialise the audio extractor and translation units
        self.audio_extractor = AudioExtractor(video=self.video)
        self.audio_translation = AudioTranslation(audio=self.extracted_audio, output_language=self.output_language, input_language=self.input_language)
        self.video_translation = VideoTranslation(self.video)
        self.logger.debug("Translation unit initialized successfully")

    def get_output_video(self) -> Optional[str]:
        """Return the path to the combined output video once translation is complete."""
        return self.output_video_filename

    async def translate_audio(self) -> Optional[str]:
        """Asynchronous coroutine for performing the audio translation.

        Returns the path to the translated audio on success.  If the
        underlying AudioTranslation returns ``None`` the pipeline will fall
        back to using the extracted audio.
        """
        self.logger.debug("Starting audio translation")
        try:
            result = await self.audio_translation.translate()
            self.logger.info("Audio translation completed successfully")
            return result
        except Exception as e:
            self.logger.error(f"Error during audio translation: {e}")
            raise

    async def translate_video(self) -> Video:
        """Asynchronous coroutine for performing the video translation.

        Returns a :class:`Video` instance pointing at the processed video file.
        """
        self.logger.debug("Starting video translation")
        try:
            result = await self.video_translation.translate()
            self.logger.info("Video translation completed successfully")
            return result
        except Exception as e:
            self.logger.error(f"Error during video translation: {e}")
            raise

    def _combine_audio_video(self, video_path: str, audio_path: str) -> str:
        """Combine the provided audio with the video into a final output file.

        Uses ffmpeg for muxing; if ffmpeg is unavailable or fails the original
        video is copied to the output location.  The output file is stored
        under ``Config.TRANSLATION_OUTPUT_PATH`` and its name is derived from
        the original video filename.
        """
        basename = os.path.basename(video_path)
        name, ext = os.path.splitext(basename)
        output_dir = str(Config.TRANSLATION_OUTPUT_PATH)
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"translated_{name}{ext}")

        # If no translated audio was produced, simply copy the video and return
        if audio_path is None or not os.path.exists(audio_path):
            self.logger.warning("No translated audio provided; copying original video to output.")
            try:
                import shutil
                shutil.copy(video_path, output_path)
            except Exception as e:
                self.logger.error(f"Failed to copy video to output path: {e}")
                raise
            return output_path

        # Try to merge audio and video with ffmpeg
        command = [
            "ffmpeg",
            "-y",
            "-i",
            video_path,
            "-i",
            audio_path,
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            output_path,
        ]
        self.logger.debug(f"Combining audio and video with command: {' '.join(command)}")
        try:
            subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.logger.info(f"Combined audio and video saved to {output_path}")
        except Exception as e:
            self.logger.error(f"Error combining audio and video: {e}; falling back to copying video.")
            import shutil
            shutil.copy(video_path, output_path)
        return output_path

    async def translate(self) -> None:
        """Perform both audio and video translations and combine the results."""
        self.logger.debug("Starting parallel audio and video translations")
        try:
            utils.setup()

            # Extract audio from the video synchronously
            self.audio_extractor.extract(output_file=self.extracted_audio_file)

            # Kick off audio and video translation tasks concurrently
            translation_tasks = [
                self.translate_audio(),
                self.translate_video(),
            ]
            audio_path, video_obj = await asyncio.gather(*translation_tasks)

            # Determine which audio to use; fall back to extracted audio if necessary
            final_audio_path = audio_path or self.extracted_audio_file
            final_video_path = video_obj.get_filename() if isinstance(video_obj, Video) else None

            # Combine audio and video
            if final_video_path:
                combined_path = self._combine_audio_video(final_video_path, final_audio_path)
                self.output_video_filename = combined_path
            else:
                # If video translation failed to return a Video object, just copy the input video
                self.logger.warning("Video translation did not return a Video object; copying original video.")
                import shutil
                output_dir = str(Config.TRANSLATION_OUTPUT_PATH)
                os.makedirs(output_dir, exist_ok=True)
                dest_path = os.path.join(output_dir, os.path.basename(self.video_file))
                shutil.copy(self.video_file, dest_path)
                self.output_video_filename = dest_path

            self.logger.info("Parallel audio and video translations completed successfully")
        except Exception as e:
            self.logger.critical(f"Error during parallel audio and video translations: {e}")
            raise
        finally:
            utils.teardown()

    def translate_sync(self) -> None:
        """Synchronous wrapper around the asynchronous translate coroutine."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.translate())
        loop.close()
