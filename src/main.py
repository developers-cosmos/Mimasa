#!/usr/bin/env python3
"""
main.py

This module contains the main entry point for the program. It is responsible for
initializing all necessary components and executing the main logic of the program.
"""
import os
import glob
import sys
import logging
import asyncio
from subprocess import Popen, PIPE

from src.common.config import Config
from src.common.audio import Audio
from src.common.video import Video
from src.utils import utils

logging.basicConfig(
    stream=sys.stdout, level=Config.LOG_LEVEL, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


async def run_face_detection():
    """
    Async function to run face detection logic
    """
    logging.info("Starting Face Detection")
    video = Video(Config.VIDEO_INPUT_FILENAME, Config.INPUT_LANGUAGE)
    video_detector = utils.get_detector(detector_type=Config.VIDEO_DETECTOR)

    try:
        await utils.detect_faces_in_realtime(detector=video_detector, video=video)
    except Exception as e:
        logging.error(f"Error in Face Detection: {e}")


async def run_audio_separation():
    """
    Async function to run audio separation logic
    """
    logging.info("Starting Audio Separation")
    audio = Audio(Config.AUDIO_INPUT_FILENAME, Config.INPUT_LANGUAGE)
    separator = utils.get_audio_separator(Config.AUDIO_SEPARATOR)

    try:
        await separator.separate_vocals_and_music(audio=audio)
    except Exception as e:
        logging.error(f"Error in Audio Separation: {e}")


async def main():
    """
    Main function to run the async functions concurrently
    """
    input_coroutines = [run_face_detection(), run_audio_separation()]
    await asyncio.gather(*input_coroutines, return_exceptions=True)


def setup():
    # create folder for logs storage
    if not os.path.exists(Config.LOGS_FOLDER_PATH):
        os.mkdir(Config.LOGS_FOLDER_PATH)
    else:
        logs = glob.glob(f"{Config.LOGS_FOLDER_PATH}/*")
        for log in logs:
            os.remove(log)

    # redirect stderr, stdout to a file
    saveerr = sys.stderr
    fsock1 = open(f"{Config.LOGS_FOLDER_PATH}/stderr.log", "w")
    sys.stderr = fsock1

    saveout = sys.stdout
    fsock2 = open(f"{Config.LOGS_FOLDER_PATH}/stdout.log", "w")
    sys.stdout = fsock2


if __name__ == "__main__":
    setup()
    asyncio.run(main())
