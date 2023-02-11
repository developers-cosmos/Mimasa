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
def main():
    """
    Main function to run the async functions concurrently
    """
    input_video_file_path = Config.TRANSLATION_VIDEO_INPUT_FILENAME
    input_langauge = Config.INPUT_LANGUAGE
    target_language = Config.TARGET_LANGUAGE
    try:
        main_logger.info("Initializing Mimasa Application...")
        video = Video(file_path=input_video_file_path, language=input_langauge)
        translation_unit = Translation(video=video, output_language=target_language, input_language=input_langauge)
        main_logger.info("Mimasa Application initialized successfully")

        main_logger.info("Translation started...")
        asyncio.run(translation_unit.translate())
        main_logger.info("Translation finished successfully")
    except:
        main_logger.critical("Translation failed. Shutting down Mimasa application!!")


if __name__ == "__main__":
   main()
