#!/usr/bin/env python3
"""
AudioExtractor Class
"""
from src.common.libraries import AudioSegment, Video, Logger


class AudioExtractor:
    """Class for extracting audio from a video file"""

    def __init__(self, video: Video):
        """
        Initialize an AudioExtractor object with a video file

        :param video: a valid Video object
        """
        self.video_file = video.get_filename()
        self.logger = Logger(self.__class__.__name__)
        self.logger.add_file_handler("audio_extractor.log")

    def extract(self, output_file):
        """Extract audio from the video file and save it to the specified file"""
        self.logger.debug(f"Extracting audio from video file: {self.video_file}")
        try:
            video = AudioSegment.from_file(self.video_file, self.video_file.split(".")[-1])
            video.export(output_file, format="wav")
            self.logger.info(f"Audio extracted successfully and saved to file: {output_file}")
        except Exception as e:
            self.logger.error(f"Error during audio extraction: {e}")
