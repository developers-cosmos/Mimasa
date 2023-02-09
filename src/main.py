#!/usr/bin/env python3
"""
main.py

This module contains the main entry point for the program. It is responsible for
initializing all necessary components and executing the main logic of the program.
"""
import os
import glob
import sys
import asyncio
from subprocess import Popen, PIPE

from src.common.config import Config
from src.common.logger import Logger
from src.common.audio import Audio
from src.common.video import Video
from src.utils.utils import track_performance
from src.facedetector.utils import get_face_detector, detect_faces_in_realtime, get_async_face_detector
from src.audioseparator.utils import get_audio_separator
from src.facedetector.async_face_detector import AsyncFaceDetector

main_logger = Logger("MAIN")
main_logger.add_file_handler("main.log")


async def run_face_detection():
    """
    Async function to run face detection logic
    """
    main_logger.info("Starting Face Detection")
    video = Video(Config.VIDEO_INPUT_FILENAME, Config.INPUT_LANGUAGE)
    face_detector = get_face_detector(detector_type=Config.VIDEO_DETECTOR)

    try:
        if not Config.FACE_DETECTION_ASYNC_ENABLED:
            await detect_faces_in_realtime(detector=face_detector, video=video)
        else:
            async_face_detector = AsyncFaceDetector(video=video)
            async_approach_type = get_async_face_detector(Config.VIDEO_ASYNC_FACE_DETECTOR)
            await async_face_detector.detect_faces_in_realtime(
                async_approach=async_approach_type, face_detector=face_detector
            )
    except Exception as e:
        main_logger.error(f"Error in Face Detection: {e}")
        raise


async def run_audio_separation():
    """
    Async function to run audio separation logic
    """
    main_logger.info("Starting Audio Separation")
    audio = Audio(Config.AUDIO_INPUT_FILENAME, Config.INPUT_LANGUAGE)
    separator = get_audio_separator(Config.AUDIO_SEPARATOR)

    try:
        await separator.separate_vocals_and_music(audio=audio)
    except Exception as e:
        main_logger.error(f"Error in Audio Separation: {e}")


@track_performance
async def main():
    """
    Main function to run the async functions concurrently
    """
    input_coroutines = [run_face_detection(), run_audio_separation()]
    await asyncio.gather(*input_coroutines)


def setup():
    # create folder for logs storage
    if not os.path.exists(Config.LOGS_FOLDER_PATH):
        os.mkdir(Config.LOGS_FOLDER_PATH)
    else:
        logs = glob.glob(f"{Config.LOGS_FOLDER_PATH}/*")
        for log in logs:
            if os.path.exists(log):
                try:
                    os.remove(log)
                except:
                    pass

    if Config.REDIRECT_STDOUT_TO_FILE:
        global saveout
        saveout = sys.stdout
        fsock2 = open(f"{Config.LOGS_FOLDER_PATH}/stdout.log", "w")
        sys.stdout = fsock2

    if Config.REDIRECT_STDERR_TO_FILE:
        global saveerr
        saveerr = sys.stderr
        fsock1 = open(f"{Config.LOGS_FOLDER_PATH}/stderr.log", "w")
        sys.stderr = fsock1


def teardown():
    if Config.REDIRECT_STDOUT_TO_FILE:
        sys.stdout = saveout

    if Config.REDIRECT_STDERR_TO_FILE:
        sys.stderr = saveerr


if __name__ == "__main__":
    setup()
    asyncio.run(main())
    teardown()
