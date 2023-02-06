#!/usr/bin/env python3
"""
This file contains utility functions that are commonly used throughout the application.
"""

import logging
from datetime import datetime

formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(funcName)s: %(message)s", "%d-%m-%Y %H:%M:%S")


def get_current_time():
    """Returns the current time as a string"""
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def setup_logger(logger_name: str, log_file: str, log_level: int = logging.WARNING):
    """To setup as many loggers"""

    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)
    logger.addHandler(handler)

    return logger
