import os
import asyncio
from src.facedetector import utils
from src.facedetector.async_face_detector import AsyncFaceDetector
from src.common.libraries import Video, Config


def face_detection_service(
    video_filepath: str, destination: str, async_enabled: bool, async_type: str, detector_type: str
):
    try:
        video = Video(video_filepath)
        face_detector = utils.get_face_detector(detector_type=detector_type)
        if not async_enabled:
            output_video = asyncio.run(
                utils.detect_faces_in_realtime(detector=face_detector, video=video, destination=destination)
            )
        else:
            async_face_detector = AsyncFaceDetector(video=video, destination=destination)
            async_approach = utils.get_async_face_detector(async_type)
            output_video = asyncio.run(
                async_face_detector.detect_faces_in_realtime(async_approach=async_approach, face_detector=face_detector)
            )
        video_filepath = output_video.get_filename()
        return {
            "video_filename": os.path.basename(video_filepath),
        }
    except Exception as e:
        return {
            "error": str(e),
            "exc_type": type(e).__name__,
        }
