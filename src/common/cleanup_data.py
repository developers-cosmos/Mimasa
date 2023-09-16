#!/usr/bin/env python3
"""
cleanup_data.py

This module contains the main entry point for cleaning the data downloaded using download_data.py
"""

import os

from src.common.config import Config


def remove_file(file_path: str):
    """
    Remove a file if it exists
    """

    if os.path.exists(file_path):
        os.remove(file_path)


def cleanup_models():
    """
    Function to cleanup models
    """
    models = ["nussl"]

    for model in models:
        if model == "nussl":
            output_path = Config.MODEL_NUSSL_PATH
            remove_file(output_path)


def cleanup_audios():
    """
    Function to cleanup input audios
    """

    audio_path = Config.AUDIO_INPUT_PATH
    audios = {
        "input.wav": "187smy0j5CCGhQlf-AheLz2pvIP-3DR3c",
        "input1.wav": "1ExFxlJkUmYCtgMkWdOiDP_y3daSiB1PL",
        "input2.wav": "14HJ7OxsfUpU2taNKrX-ehC6AonfjaxVi",
    }

    for filename, _ in audios.items():
        remove_file(audio_path / filename)


def cleanup_videos():
    """
    Function to cleanup input videos
    """

    video_path = Config.VIDEO_INPUT_PATH
    videos = {
        "input1.mp4": "1T-fmD9JffWdp51FS_inQuzu_FCOlVvI9",
        "input2.mp4": "1mlfGQmkhJc5jxY5RPde6eA0TZeCPTo6R",
    }

    for filename, _ in videos.items():
        remove_file(video_path / filename)


def cleanup_translations():
    """
    Function to cleanup input videos for translation app
    """

    translation_path = Config.TRANSLATION_INPUT_PATH
    videos = {
        "movie1.mp4": "14CC9hKnrOw4jSsUxUD35GWKYnQHShxKe",
        "movie2.mp4": "1PQ3t9_Uulu_GjYorv8Iur48af6fwKSyQ",
        "movie3.mp4": "1x2yrExwi9FYxMBk-O8OEvMPZA73BeTbP",
        "movie4.mp4": "1zIFR8rXwuOnF6tXkN08h7PTsqrM7WgAj",
    }

    for filename, _ in videos.items():
        remove_file(translation_path / filename)


if __name__ == "__main__":
    cleanup_models()
    cleanup_audios()
    cleanup_videos()
    cleanup_translations()
