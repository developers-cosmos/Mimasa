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

from src.common.libraries import Config, Video, Logger
from src.utils.utils import track_performance
from src.translation.translation import Translation

main_logger = Logger("MAIN")
main_logger.add_file_handler("main.log")


@track_performance
async def main():
    """
    Main function to run the async functions concurrently
    """
    try:
        main_logger.info("Initializing Mimasa Application...")
        video = Video(Config.TRANSLATION_VIDEO_INPUT_FILENAME, Config.INPUT_LANGUAGE)
        translation_unit = Translation(
            video=video, output_language=Config.TARGET_LANGUAGE, input_language=Config.INPUT_LANGUAGE
        )
        main_logger.info("Mimasa Application initialized successfully")

        main_logger.info("Translation started...")
        await translation_unit.translate()
        main_logger.info("Translation finished successfully")
    except:
        main_logger.critical("Translation failed. Shutting down Mimasa application!!")


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
