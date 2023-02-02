#!/usr/bin/env python3
"""
Audio Class
"""

class Audio:
    """
    Class representing an audio.

    Attributes:
        file_path (str): The file path of the audio.
        language (str): The language of the audio.
    """

    def __init__(self, file_path: str, language: str = "Unknown"):
        """
        The constructor for the Audio class.

        Args:
            file_path (str): The file path of the audio.
            language (str): The language of the audio.
        """
        self.file_path = file_path
        self.language = language

    def get_filename(self) -> str:
        """
        Get the file path of the audio.

        Returns:
            str: The file path of the audio.
        """
        return self.file_path

    def set_filename(self, file_path: str):
        """
        Set the file path of the audio.

        Args:
            file_path (str): The new file path of the audio.
        """
        self.file_path = file_path

    def get_language(self) -> str:
        """
        Get the language of the audio.

        Returns:
            str: The language of the audio.
        """
        return self.language

    def set_language(self, language: str):
        """
        Set the language of the audio.

        Args:
            language (str): The new language of the audio.
        """
        self.language = language
