#!/usr/bin/env python3
"""
User defined exceptions for Mimasa Application
"""

class InvalidInputError(Exception):
    """Raised when the input provided is invalid"""
    pass

class FileNotFoundError(Exception):
    """Raised when the file is not found in the specified path"""
    pass

class NetworkError(Exception):
    """Raised when there is a network error"""
    pass

class OutOfMemoryError(Exception):
    """Raised when there is not enough memory to complete the operation"""
    pass

class AudioSeparationError(Exception):
    """Raised when separation of audio to vocals and music failed"""
    pass

class FaceDetectionError(Exception):
    """Raised when face detection failed"""
    pass
