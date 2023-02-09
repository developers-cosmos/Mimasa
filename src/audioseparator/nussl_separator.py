#!/usr/bin/env python3
"""
NUSSL Class
"""

from src.audioseparator.audio_separator import AudioSeparator
from src.audioseparator.mask_inference import MaskInference
from src.common.audio import Audio
from src.common.libraries import nussl, torch
from src.common.config import Config
from src.utils import utils
from src.common.exceptions import AudioSeparationError
from src.common.logger import Logger


class NUSSL(AudioSeparator):
    """
    Implements the NUSSL audio separation algorithm
    """

    def __init__(self, model_path: str = None):
        self.separator = None
        self.vocals_path = None
        self.music_path = None
        self.estimates = {}

        self.logger = Logger(name=self.__class__.__name__)
        self.logger.add_file_handler("audio_separation.log")

        self._initialize_separator(model_path)

    def _initialize_separator(self, model_path: str = None):
        """
        Initialize the NUSSL separator with the given model path and device
        """
        try:
            self.logger.debug("NUSSL separator is loading...")

            stft_params = nussl.STFTParams(window_length=512, hop_length=128)
            nf = stft_params.window_length // 2 + 1
            nac = 1
            MaskInference.build(nf, nac, 300, 4, True, 0.3, 1, "sigmoid")

            model_path = model_path or Config.MODEL_NUSSL_PATH
            self.separator = nussl.separation.deep.DeepMaskEstimation(
                nussl.AudioSignal(), model_path=model_path, device=Config.DEVICE
            )
            self.logger.info("NUSSL separator initialized successfully")
        except Exception as e:
            self.logger.error("Failed to initialize NUSSL separator due to {}".format(str(e)))

    async def _separate_audio(self):
        """
        Separate the audio signal into vocals and music
        """
        try:
            self.logger.debug("AudioSeparation started...")
            # Perform the audio separation
            estimates = self.separator()

            # Store the separated audio signals
            self.estimates = {
                "vocals": estimates[0],
                "bass+drums+other": self.separator.audio_signal - estimates[0],
            }
            self.logger.debug("Audio separated into vocals and music")
        except Exception as e:
            self.logger.error("Failed to separate audio due to {}".format(str(e)))

    def _write_estimates_to_files(self, destination: str = None):
        """
        Write the separated audio signals to destination
        """
        try:
            self.logger.debug("Writing estimations to output files.")

            destination = destination or Config.AUDIO_OUTPUT_PATH
            filename = (
                __class__.__base__.__name__.lower() + "_" + self.__class__.__name__.lower() + utils.get_current_time()
            )
            self.vocals_path = f"{destination}/{filename}_speech.{Config.AUDIO_DEFAULT_FORMAT}"
            self.music_path = f"{destination}/{filename}_music.{Config.AUDIO_DEFAULT_FORMAT}"

            self.logger.info("Filename for output vocals: %s" % self.vocals_path)
            self.logger.info("Filename for output music: %s" % self.music_path)

            speech_signal = self.estimates["vocals"]
            speech_signal.write_audio_to_file(self.vocals_path)

            music_signal = self.estimates["bass+drums+other"]
            music_signal.write_audio_to_file(self.music_path)
            self.logger.debug("Estimates written to files")
        except Exception as e:
            self.logger.error("Failed to write estimates to files due to {}".format(str(e)))

    async def separate_vocals_and_music(self, audio: Audio, destination: str = None):
        """
        Separates the vocals and music from the audio asynchronously
        """
        try:
            self.logger.info("Filename for input audio: %s" % audio.get_filename())

            # Set the audio signal to be separated
            self.separator.audio_signal = nussl.AudioSignal(
                audio.get_filename(), sample_rate=Config.ORIGINAL_SAMPLING_RATE
            )
            # await asyncio.run_coroutine_threadsafe(self._separate_audio(), loop=asyncio.get_event_loop())
            await self._separate_audio()
            self._write_estimates_to_files(destination)
        except Exception as e:
            self.logger.error("Failed to separate vocals and music due to {}".format(str(e)))
            raise AudioSeparationError(e)

    def get_vocals(self) -> Audio:
        """
        Get the separated vocals from the audio
        """
        # construct the Audio from vocals_path
        Vocal = Audio(self.vocals_path)
        return Vocal

    def get_music(self) -> Audio:
        """
        Get the separated music from the audio
        """
        # construct the Audio from music_path
        Music = Audio(self.music_path)
        return Music
