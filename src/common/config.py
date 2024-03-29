#!/usr/bin/env python3
"""
Config Class
"""

import os
import sys
from pathlib import Path

import torch


def is_venv():
    """Returns true if the current env is a venv"""
    return hasattr(sys, "real_prefix") or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix)


class Config:
    # declare all the configuration parameters as static variables

    # the application is expected to run from root directory
    # BASE_DIR = Path(__file__).resolve().parent.parent.parent  # Path(os.getcwd())
    BASE_DIR = Path(os.path.dirname(sys.prefix)) if is_venv() else Path(__file__).resolve().parent.parent.parent
    os.chdir(BASE_DIR)

    # # api keys for Mimasa
    # API_KEY = "your-api-key"
    # API_URL = "https://api.mimasa.com"

    # user inputs
    INPUT_LANGUAGE = "en-US"
    TARGET_LANGUAGE = "hi-IN"

    # common settings
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    FACE_DETECTION_ASYNC_ENABLED = True

    ORIGINAL_SAMPLING_RATE = 44100
    AUDIO_DEFAULT_FORMAT = "wav"
    VIDEO_DEFAULT_FORMAT = "mp4"

    # Data Folder
    DATA_FOLDER = BASE_DIR / "data"

    ## Translation Unit Settings
    TRANSLATION_INPUT_PATH = DATA_FOLDER / "translation" / "inputs"
    TRANSLATION_OUTPUT_PATH = DATA_FOLDER / "translation" / "outputs"
    TRANSLATION_VIDEO_INPUT_FILENAME = TRANSLATION_INPUT_PATH / "movie4.mp4"

    ## Video Options
    VIDEO_INPUT_PATH = DATA_FOLDER / "videos" / "inputs"
    VIDEO_OUTPUT_PATH = DATA_FOLDER / "videos" / "outputs"
    VIDEO_INPUT_FILENAME = VIDEO_INPUT_PATH / "input2.mp4"
    VIDEO_FORMATS = ["mp4"]
    VIDEO_DETECTOR = "MTCNN"  # possible values: ["ViolaJones", "MTCNN", "SSD", "YOLO", "RetinaFace"]
    VIDEO_ASYNC_FACE_DETECTOR = "AsyncTaskFaceDetector"  # possible values: ["AsyncTaskFaceDetector", "ConcurrentFuturesFaceDetector", "AsyncIOAndCPUFaceDetector"]
    FACE_DETECTOR_NUM_WORK_THREADS = 3  # min(32, (os.cpu_count() or 1) + 4)

    ## Datasets

    ## Audio Options
    AUDIO_INPUT_PATH = DATA_FOLDER / "audios" / "inputs"
    AUDIO_OUTPUT_PATH = DATA_FOLDER / "audios" / "outputs"
    AUDIO_INPUT_FILENAME = AUDIO_INPUT_PATH / "input.wav"
    AUDIO_FORMATS = ["wav", "mp3"]
    AUDIO_SEPARATOR = "NUSSL"

    ## Pre-Trained Models
    MODELS_PATH = DATA_FOLDER / "models"

    ### Audio
    #### Audio Separator

    ##### NUSSL
    MODEL_NUSSL_PATH = MODELS_PATH / "nussl" / "checkpoints" / "best.model.pth"

    # logging configuration
    LOGS_FOLDER_PATH = BASE_DIR / "logs"
    LOG_LEVEL = "debug"  # possible options: ["debug", "info", "warning", "error", "critical",]
    REDIRECT_STDOUT_TO_FILE = True
    REDIRECT_STDERR_TO_FILE = False

    # declare a private constructor to prevent instantiation of this class
    def __init__(self):
        raise NotImplementedError("Config is a static class and cannot be instantiated.")
