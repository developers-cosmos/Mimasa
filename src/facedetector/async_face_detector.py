#!/usr/bin/env python3
"""
This module contains the AsyncFaceDetector class, which is used as a base class to detect faces
in a given video asynchronously
"""
import asyncio
import os
from src.common.libraries import *
from src.utils.utils import setup_logger, get_current_time
from src.common.config import Config


class AsyncFaceDetector:
    def __init__(self, video: Video):
        self.face_detector = None
        self.input_file = video.get_filename()
        self.output_file = ""
        self.logger = None
        self.video_capture = None
        self.video_writer = None
        self.total_frames = 0

        # Create a queue to store the frames from the video
        self.frames_queue = asyncio.Queue()

        # Create a list to track the frames and faces
        self.frame_with_faces = []

        # create a queue to store the frames with faces and index to track the order of the frames
        self.frame_with_faces_queue = asyncio.Queue()

        # create a list to store the final processed frames
        self.final_frames = None

        self.writer_task_running = True
        self.num_writer_workers = Config.FACE_DETECTOR_NUM_WORK_THREADS
        self.num_processing_workers = 2

        self._initialize_detector()

    def _initialize_detector(self):
        if os.path.exists(Config.VIDEO_OUTPUT_PATH) and os.path.exists(self.input_file):
            out_filename = (
                "FaceDetector".lower()
                + "_"
                + Config.VIDEO_DETECTOR.lower()
                + "_"
                + get_current_time()
                + "."
                + Config.VIDEO_DEFAULT_FORMAT
            )
            self.output_file = Config.VIDEO_OUTPUT_PATH / out_filename

            # setup logging
            log_file = f"{Config.LOGS_FOLDER_PATH}/face_detector.log"
            self.logger = setup_logger(self.__class__.__name__, log_file, Config.LOG_LEVEL)
            self.logger.debug("AsyncFaceDetector is initialized successfully")
        else:
            self.logger.error("Failed to initialize face detection. Check the input & output vide paths")
            raise FaceDetectionError("Could not find input video file or video output path.")

    def _initialize_face_detection(self, detector_type):
        self.logger.debug("Initializing face detection...")

        try:
            # get the detector from its type
            self.face_detector = detector_type

            # Create an instance of the video capture object
            self.video_capture = cv2.VideoCapture(str(self.input_file))

            # Check if the video capture object is opened
            if not self.video_capture.isOpened():
                self.logger.error("Unable to open video file")
                return

            fourcc = cv2.VideoWriter_fourcc("m", "p", "4", "v")
            video_fps = (self.video_capture.get(cv2.CAP_PROP_FPS),)
            self.total_frames = int(self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
            height = self.video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
            width = self.video_capture.get(cv2.CAP_PROP_FRAME_WIDTH)

            self.logger.info(f"Frame Per second: {video_fps}")
            self.logger.info(f"Total Frames: {self.total_frames}")
            self.logger.info(f"Height: {height}, Width: {width}")

            self.video_writer = cv2.VideoWriter(
                str(self.output_file),
                apiPreference=0,
                fourcc=fourcc,
                fps=video_fps[0],
                frameSize=(int(width), int(height)),
            )
            self.logger.debug("Initialization done. Video is taken from input folder")
        except Exception as e:
            self.logger.error("Failed to initialize face detection system due to {}".format(str(e)))

    def _draw_bounding_boxes(self, frame, faces):
        """draw bounding boxes with the given faces on a given frame"""
        for face in faces:
            if self.face_detector.__class__.__name__ == "ViolaJones":
                x, y, w, h = face
            else:
                x, y, w, h = face["box"]
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        return frame

    # async def detect_faces_in_realtime(self, face_detector, async_approach):
    #     """
    #     Detect faces in a video in real-time and write the frames with faces to an output video file
    #     """
    #     print(
    #         f"Detecting faces in video using face detector: {face_detector.__class__.__name__} and approach: {async_approach.__class__.__name__}"
    #     )

    #     await async_approach.detect_faces_in_realtime(face_detector)