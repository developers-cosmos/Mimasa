#!/usr/bin/env python3
"""
Video Class
"""


class Video:
    """
    Class representing a video.

    Attributes:
        file_path (str): The file path of the video.
        language (str): The language of the video.
    """

    def __init__(self, file_path: str, language: str = "Unknown"):
        """
        The constructor for the Video class.

        Args:
            file (str): The file path of the video.
            language (str): The language of the video.
        """
        self.file_path = file_path
        self.language = language

    def get_filename(self) -> str:
        """
        Get the file path of the video.

        Returns:
            str: The file path of the video.
        """
        return str(self.file_path)

    def set_filename(self, file_path: str):
        """
        Set the file path of the video.

        Args:
            file (str): The new file path of the video.
        """
        self.file_path = file_path

    def get_language(self) -> str:
        """
        Get the language of the video.

        Returns:
            str: The language of the video.
        """
        return self.language

    def set_language(self, language: str):
        """
        Set the language of the video.

        Args:
            language (str): The new language of the video.
        """
        self.language = language
