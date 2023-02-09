#!/usr/bin/env python3
"""
This module contains the AsyncTaskFaceDetector class.
This class uses the asyncio library for concurrency

Functionality:
------------------------------------------------------------------------------------------------

1. A video is read frame by frame and the frames are added to a async queue.
2. The frames are processed concurrently using asyncio.
3. For each frame, the face detection function is called, which detects faces in the frame.
4. The frames with faces stored in list are written to video writer.

Note: (4) write operation is performed after all the frames have been processed
(4) is not asynchronously performed

Performance:
------------------------------------------------------------------------------------------------
Below are the performance metrics of AsyncTaskFaceDetector:

1. Input video details: video of length 6 seconds

Frame Per second: (23.976023976023978,)
Total Frames: 146
Height: 720.0, Width: 1280.0

Peformance:

Execution time of 'main': 93.81 seconds
Memory usage of 'main': 639.89 MB
CPU usage of 'main': 20.18%
----------------------------------------------------------------------------------------------
2. Input video details: video of length 16 seconds

Frame Per second: (23.976023976023978,)
Total Frames: 388
Height: 720.0, Width: 1280.0

Performance:

Execution time of 'main': 346.64 seconds
Memory usage of 'main': 1445.79 MB
Average CPU usage of 'main': 20.62%
"""

import asyncio

from src.common.libraries import *


class AsyncTaskFaceDetector:
    def __init__(self):
        self.face_detector = None

        # Create a list to track the frames and faces
        self.frame_with_faces = []

    def _initialize(self, async_detector, face_detector):
        self.face_detector = face_detector

        # get the members of AsyncFaceDetector instance
        for attr in dir(async_detector):
            if not attr.startswith("__"):
                setattr(self, attr, getattr(async_detector, attr))

    async def _read_frames(self):
        """Read frames from the input video stream and put them on the queue"""
        while True:
            ret, frame = self.video_capture.read()
            if not ret:
                self.logger.debug("Unable to retrieve frame from video stream, breaking loop")
                break
            await self.frames_queue.put(frame)
            self.logger.debug("Put frame on queue")

    async def _detect_faces(self, frame_index: int):
        """Detect faces in the given frame index and populate frames and faces information"""
        frame = await self.frames_queue.get()
        if frame is None:
            self.logger.debug("Queue is empty, breaking loop")
            return
        # Detect faces in the frame
        faces = self.face_detector.detect_faces(frame)
        # Add the frame with faces to frame_with_faces
        self.frame_with_faces[frame_index] = [frame, faces]
        self.logger.debug(f"Appended frame with faces to frame_with_faces at index {frame_index}")

    async def _detect_faces_with_async_tasks(self):
        """frames are processed concurrently"""
        tasks = []
        for i in range(0, self.total_frames):
            task = asyncio.create_task(self._detect_faces(i))
            tasks.append(task)
        await asyncio.gather(*tasks)

    def _write_frames_to_output(self):
        """Write the frames with faces to an output video"""
        for i, f in enumerate(self.frame_with_faces):
            frame = f[0]
            faces = f[1]
            if faces:
                self._draw_bounding_boxes(frame, faces)
            self.video_writer.write(frame)
            self.logger.debug(f"Wrote frame {i} with faces to output video")
        self.video_writer.release()
        self.logger.info("Finished writing to output video")

    async def detect_faces_in_realtime(self, async_detector, face_detector):
        """
        Detect faces in a video in real-time and write the frames with faces to an output video file
        """
        self._initialize(async_detector, face_detector)
        try:
            self.frame_with_faces = [None] * self.total_frames

            logging.info("Face detection started...")

            # Start the tasks to read frames, detect faces, and write to the output to video file
            await asyncio.gather(
                self._read_frames(),
                self._detect_faces_with_async_tasks(),
            )
            self._write_frames_to_output()
        except Exception as e:
            self.logger.error("Failed to detect faces from the given video file due to {}".format(str(e)))
            raise FaceDetectionError(str(e))
        finally:
            self.video_capture.release()
            cv2.destroyAllWindows()

            if self.video_writer:
                self.video_writer.release()

        self.logger.debug("Finished detecting faces in real-time")
