#!/usr/bin/env python3
"""
AudioSeparator Interface
"""

from src.common.audio import Audio

class AudioSeparator:
    """
    AudioSeparator interface with following functionalities:
        separateVocalsAndMusic(audio: Audio)
        getVocals(): Audio
        getMusic(): Audio
    """
    def separate_vocals_and_music(self, audio: Audio):
        """
        Separate vocals and music from the given audio
        """
        raise NotImplementedError

    def get_vocals(self):
        """
        Get the separated vocals from the audio
        """
        raise NotImplementedError

    def get_music(self):
        """
        Get the separated music from the audio
        """
        raise NotImplementedError
