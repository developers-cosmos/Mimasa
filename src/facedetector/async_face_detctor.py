#!/usr/bin/env python3
"""
This module contains the AsyncFaceDetector class, which is used to detect faces
in a given video asynchronously
"""
import asyncio
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.common.libraries import *
from src.utils.utils import setup_logger, get_current_time


class AsyncQueue:
    def __init__(self):
        self._queue = []
        self._lock = asyncio.Lock()

    async def insert_at(self, index, item):
        async with self._lock:
            self._queue.insert(index, item)

    async def get_at(self, index):
        async with self._lock:
            return self._queue[index]


class AsyncFaceDetector:
    def __init__(self, video: Video):
        self.face_detector = None
        self.input_file = video.get_filename()
        self.output_file = ""
        self.logger = None
        self.video_capture = None
        self.video_writer = None
        self.total_frames = 0
        self.num_workers = 4

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
            self.logger.info(f"Height: {height} \nWidth: {width}")

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

    async def _read_frames(self, frames_queue):
        """Read frames from the input video stream and put them on the queue"""
        while True:
            ret, frame = self.video_capture.read()
            if not ret:
                self.logger.debug("Unable to retrieve frame from video stream, breaking loop")
                break
            await frames_queue.put(frame)
            self.logger.debug("Put frame on queue")

    def _draw_bounding_boxes(self, frame, faces):
        for face in faces:
            if self.face_detector.__class__.__name__ == "ViolaJones":
                x, y, w, h = face
            else:
                x, y, w, h = face["box"]
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        return frame

    async def _detect_face_task(self, frame_index, frames_queue, frame_with_faces):
        frame = await frames_queue.get()
        if frame is None:
            self.logger.debug("Queue is empty, breaking loop")
            return
        # Detect faces in the frame
        faces = self.face_detector.detect_faces(frame)
        # Add the frame with faces to frame_with_faces
        frame_with_faces[frame_index] = [frame, faces]
        self.logger.debug(f"Appended frame with faces to frame_with_faces at index {frame_index}")

    async def _detect_faces_with_async_tasks(self, frames_queue, frame_with_faces):
        tasks = []
        for i in range(0, self.total_frames):
            task = asyncio.create_task(self._detect_face_task(i, frames_queue, frame_with_faces))
            tasks.append(task)
        await asyncio.gather(*tasks)

    # async def _detect_faces_with_concurrent_futures(self, frames_queue, frame_with_faces):
    #     with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
    #         frame = await frames_queue.get()
    #         for frame_index in range(self.total_frames):
    #         futures = [executor.submit(self._detect_face_future, frame_index, frames_queue) for frame_index, frame in enumerate(frames_queue)]
    #         for future in as_completed(futures):
    #             frame_index, result = future.result()
    #             frame_with_faces[frame_index] = result
    #     return frame_with_faces

    def _detect_future_face(self, frame_index, frames_queue, frame_with_faces):
        # TODO: check if get_nowait() can be used here
        frame = frames_queue.get_nowait()
        if frame is None:
            self.logger.debug("Queue is empty, breaking loop")
            return
        # Detect faces in the frame
        faces = self.face_detector.detect_faces(frame)
        # Add the frame with faces to frame_with_faces
        frame_with_faces[frame_index] = [frame, faces]
        self.logger.debug(f"Appended frame with faces to frame_with_faces at index {frame_index}")

    async def _detect_faces_with_concurrent_futures(self, frames_queue, frame_with_faces):
        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            loop = asyncio.get_event_loop()
            futures = [
                loop.run_in_executor(executor, self._detect_future_face, i, frames_queue, frame_with_faces)
                for i in range(self.total_frames)
            ]
            for f in asyncio.as_completed(futures):
                await f

    def _write_to_output(self, frame_with_faces):
        """Write the frames with faces to an output video file"""
        for i, f in enumerate(frame_with_faces):
            frame = f[0]
            faces = f[1]
            if faces:
                self._draw_bounding_boxes(frame, faces)
            self.video_writer.write(frame)
            self.logger.debug(f"Wrote frame {i} with faces to output video")
        self.video_writer.release()
        self.logger.info("Finished writing to output video")

    async def detect_faces_in_realtime(self, detector):
        """
        Detect faces in a video in real-time and write the frames with faces to an output video file
        """
        try:
            # initialize the face detection
            self._initialize_face_detection(detector)

            # Create a queue to store the frames
            frames_queue = asyncio.Queue()

            # Create a list to store the frames with faces
            frame_with_faces = [None] * self.total_frames

            # Start the tasks to read frames, detect faces, and write to the output file
            await asyncio.gather(
                self._read_frames(frames_queue),
                self._detect_faces_with_concurrent_futures(frames_queue, frame_with_faces),
                return_exceptions=True,
            )
            self._write_to_output(frame_with_faces)
        except Exception as e:
            self.logger.error("Failed to detect faces from the given video file due to {}".format(str(e)))
            raise FaceDetectionError(str(e))
        finally:
            self.video_capture.release()
            cv2.destroyAllWindows()

            if self.video_writer:
                self.video_writer.release()

        self.logger.debug("Finished detecting faces in real-time")
