#!/usr/bin/env python3
"""
VideoTranslation class is the main entry point for the video related processing.
"""
from src.common.libraries import Video, Logger, Config
from src.facedetector.async_face_detector import AsyncFaceDetector
from src.facedetector import utils


class VideoTranslation:
    """Class for translating faces in a video file"""

    def __init__(self, video: Video):
        """
        Initialize a VideoTranslation object with a video file

        :param video_file: The path to the video file
        """
        self.video = video
        self.video_file = video.get_filename()
        self.face_detector = None
        self.async_face_detector = None
        self.async_approach_type = None

        self.logger = Logger(self.__class__.__name__)
        self.logger.add_file_handler("video_translation.log")

        self._initialize()

    def _initialize(self):
        self.logger.debug("Initializing video translation unit...")
        self.face_detector = utils.get_face_detector(detector_type=Config.VIDEO_DETECTOR)
        if Config.FACE_DETECTION_ASYNC_ENABLED:
            self.async_face_detector = AsyncFaceDetector(video=self.video)
            self.async_approach_type = utils.get_async_face_detector(Config.VIDEO_ASYNC_FACE_DETECTOR)
        self.logger.debug("Video translation unit initialized successfully")

    async def translate(self):
        """Asynchronous coroutine for performing the video translation"""
        self.logger.debug(f"Starting video translation for file: {self.video_file}")
        try:
            if not Config.FACE_DETECTION_ASYNC_ENABLED:
                result = await utils.detect_faces_in_realtime(detector=self.face_detector, video=self.video)
            else:
                result = await self.async_face_detector.detect_faces_in_realtime(
                    async_approach=self.async_approach_type, face_detector=self.face_detector
                )
            self.logger.info(f"Video translation completed successfully for file: {self.video_file}")
            return result
        except Exception as e:
            self.logger.error(f"Error during video translation for file: {self.video_file}: {e}")
            raise
