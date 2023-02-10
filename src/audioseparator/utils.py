#!/usr/bin/env python3
"""
This file contains utility functions that are commonly used for audio separation.
"""

from src.audioseparator import nussl_separator


def get_audio_separator(separator_type: str = None, model_path: str = None):
    """
    This function is used to get the AudioSeparator object based on the separator_type.

    Parameters:
    separator_type (str): type of separator. It should be one of the following
    ["NUSSL"]

    Returns:
    object: separator object
    """
    if separator_type == "NUSSL":
        return nussl_separator.NUSSL(model_path)
    else:
        raise ValueError(f"Invalid separator type: {separator_type}")
