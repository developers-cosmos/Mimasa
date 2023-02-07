#!/usr/bin/env python3
"""
This module contains the AsyncIOAndCPUFaceDetector class.
This class uses the asyncio library and concurrent futures for concurrency

Functionality:

1. A video is read frame by frame and the frames are added to a async queue.
2. The frames are processed concurrently using concurrent futures and added to a output async queue.
3. For each frame, the face detection function is called, which detects faces in the frame.
4. The frames with faces stored in list are written to final_frames (with boxes) as soon as the output queue is available.
5. All the processed frames are written to video writer

Note: (4) write operation is performed asynchronously

Background:

1. We can use asynchronous programming to handle the I/O-bound tasks of reading and writing frames,
as these tasks can take a significant amount of time and blocking the main thread will lead to slowdowns.
The asyncio library is used.

2. For the CPU-bound task of detecting faces, we can use multithreading to allow multiple threads to run
in parallel, taking advantage of multiple CPU cores. The concurrent.futures library is used.

3. By using a combination of asynchronous programming and multithreading, we can ensure that your video
processing code runs efficiently and quickly,taking full advantage of both I/O and CPU resources

Performance:
------------------------------------------------------------------------------------------------
Below are the performance metrics of AsyncIOAndCPUFaceDetector:

1. Input video details: video of length 6 seconds

Frame Per second: (23.976023976023978,)
Total Frames: 146
Height: 720.0, Width: 1280.0
num_of_worker_threads: 4

Peformance:

Execution time of 'main': 116.27 seconds
Memory usage of 'main': 643.96 MB
Average CPU usage of 'main': 22.99%
----------------------------------------------------------------
2. Input video details: video of length 16 seconds

Frame Per second: (23.976023976023978,)
Total Frames: 388
Height: 720.0, Width: 1280.0
number of worker threads: 8

Performance:

Execution time of 'main': 225.08 seconds
Memory usage of 'main': 1588.00 MB
Average CPU usage of 'main': 41.65%
"""

import asyncio
from src.facedetector.async_face_detector import AsyncFaceDetector

from src.common.libraries import *
from concurrent.futures import ThreadPoolExecutor


class AsyncIOAndCPUFaceDetector(AsyncFaceDetector):
    def __init__(self, video: Video):
        super().__init__(video)

    async def _read_frames(self):
        """Read frames from the input video stream and put them on the queue"""
        while True:
            ret, frame = self.video_capture.read()
            if not ret:
                self.logger.debug("Unable to retrieve frame from video stream, breaking loop")
                break
            await self.frames_queue.put(frame)
            self.logger.debug("Put frame on queue")

    def _detect_and_enqueue_faces(self, frame_index: int):
        """Detect faces in the given frame index and enqueue frames and faces information"""
        try:
            frame = self.frames_queue.get_nowait()
        except asyncio.QueueEmptyException:
            self.logger.error("Queue is empty, returning back")
            return

        if frame is None:
            self.logger.debug("Queue is empty, breaking loop")
            return

        # Detect faces in the frame
        faces = self.face_detector.detect_faces(frame)
        frame_index, frame_with_faces = frame_index, (frame, faces)

        try:
            self.frame_with_faces_queue.put_nowait((frame_index, frame_with_faces))
        except asyncio.QueueFull:
            self.logger.error("Queue is full, skipping frame")
        self.logger.debug(f"Enqueued frame with faces to frame_with_faces_queue at index {frame_index}")

    async def _detect_faces_cpu_bound(self):
        """frames are processed concurrently"""
        await asyncio.sleep(2)
        with ThreadPoolExecutor(max_workers=self.num_writer_workers) as executor:
            loop = asyncio.get_event_loop()
            futures = [
                loop.run_in_executor(executor, self._detect_and_enqueue_faces, i) for i in range(self.total_frames)
            ]
            for f in asyncio.as_completed(futures):
                await f
        # sentinel for write to output from queue
        await self.frame_with_faces_queue.put(None)

    async def _write_to_output_from_queue(self):
        """Write the frames with faces to an output video file"""
        while not self.frame_with_faces_queue.empty() or self.writer_task_running:
            try:
                result = await self.frame_with_faces_queue.get()
                if result is None:
                    self.logger.debug("Unable to write frame to the video, breaking loop")
                    break
                frame_index, frame_and_faces = result
                frame, faces = frame_and_faces
                if faces:
                    frame = self._draw_bounding_boxes(frame, faces)
                self.final_frames[frame_index] = frame
                # self.video_writer.write(frame)
                self.logger.debug("Saved frame at index: %d", frame_index)
            except Exception as e:
                self.logger.error(f"Error while writing frame to video: {e}")
                break
        self.logger.info("Finished saving frames")

    def _finish_video_writer(self):
        for frame in self.final_frames:
            self.video_writer.write(frame)
        self.video_writer.release()
        logging.debug("Finished writing video to output file")

    async def detect_faces_in_realtime(self, face_detector):
        """
        Detect faces in a video in real-time and write the frames with faces to an output video file
        """
        self.logger.info(
            f"Detecting faces in video using face detector: {face_detector.__class__.__name__} and approach: {self.__class__.__name__}"
        )
        try:
            # initialize the face detection
            self._initialize_face_detection(face_detector)
            self.final_frames = [None] * self.total_frames

            tasks = [
                self._read_frames(),
                asyncio.ensure_future(self._detect_faces_cpu_bound()),
                self._write_to_output_from_queue(),
            ]
            await asyncio.gather(*tasks)

            self._finish_video_writer()
        except Exception as e:
            self.logger.error("Failed to detect faces from the given video file due to {}".format(str(e)))
            raise FaceDetectionError(str(e))
        finally:
            self.video_capture.release()
            cv2.destroyAllWindows()

            if self.video_writer:
                self.video_writer.release()

        self.logger.debug("Finished detecting faces in real-time")
