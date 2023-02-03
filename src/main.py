#!/usr/bin/env python3
"""
main.py

This module contains the main entry point for the program. It is responsible for
initializing all necessary components and executing the main logic of the program.
"""

from src.utils import utils
from src.common.config import Config
from src.common.audio import Audio
from src.common.video import Video

def main():
    """
    Main function
    """
    # TODO: Face Detection needs to be implemented correctly
    # Face Detection
    video = Video(Config.VIDEO_INPUT_FILENAME, Config.INPUT_LANGUAGE)
    video_detector = utils.get_detector(detector_type=Config.VIDEO_DETECTOR)
    utils.detect_faces_in_realtime(detector=video_detector, video=video)

    # Audio Separation
    audio = Audio(Config.AUDIO_INPUT_FILENAME, Config.INPUT_LANGUAGE)
    separator = utils.get_audio_separator(Config.AUDIO_SEPARATOR)
    separator.separate_vocals_and_music(audio=audio)

if __name__ == "__main__":
    main()
