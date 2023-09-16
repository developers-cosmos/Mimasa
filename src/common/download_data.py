#!/usr/bin/env python3
"""
download_data.py

This module contains the main entry point for downloading the data to run mimasa.
"""

from src.utils import utils
from src.common.config import Config


def download_models():
    """
    Function to download models
    """
    models = ["nussl"]

    for model in models:
        if model == "nussl":
            output_path = Config.MODEL_NUSSL_PATH
            utils.download_file_from_google_drive(
                "https://drive.google.com/uc?id=1CKwaqBj55b83qoZbg66gaUsewnQh4k8g", output_path
            )


def download_audios():
    """
    Function to download input audios
    """

    audio_path = Config.AUDIO_INPUT_PATH
    audios = {
        "input.wav": "187smy0j5CCGhQlf-AheLz2pvIP-3DR3c",
        "input1.wav": "1ExFxlJkUmYCtgMkWdOiDP_y3daSiB1PL",
        "input2.wav": "14HJ7OxsfUpU2taNKrX-ehC6AonfjaxVi",
    }

    for filename, url_id in audios.items():
        utils.download_file_from_google_drive(f"https://drive.google.com/uc?id={url_id}", audio_path / filename)


def download_videos():
    """
    Function to download input videos
    """

    video_path = Config.VIDEO_INPUT_PATH
    videos = {
        "input1.mp4": "1T-fmD9JffWdp51FS_inQuzu_FCOlVvI9",
        "input2.mp4": "1mlfGQmkhJc5jxY5RPde6eA0TZeCPTo6R",
    }

    for filename, url_id in videos.items():
        utils.download_file_from_google_drive(f"https://drive.google.com/uc?id={url_id}", video_path / filename)


def download_translations():
    """
    Function to download input videos for translation app
    """

    translation_path = Config.TRANSLATION_INPUT_PATH
    videos = {
        "movie1.mp4": "14CC9hKnrOw4jSsUxUD35GWKYnQHShxKe",
        "movie2.mp4": "1PQ3t9_Uulu_GjYorv8Iur48af6fwKSyQ",
        "movie3.mp4": "1x2yrExwi9FYxMBk-O8OEvMPZA73BeTbP",
        "movie4.mp4": "1zIFR8rXwuOnF6tXkN08h7PTsqrM7WgAj",
    }

    for filename, url_id in videos.items():
        utils.download_file_from_google_drive(f"https://drive.google.com/uc?id={url_id}", translation_path / filename)


if __name__ == "__main__":
    download_models()
    download_audios()
    download_videos()
    download_translations()
