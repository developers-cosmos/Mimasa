#!/usr/bin/env python3
"""
This file contains utility functions that are commonly used for face detection.
"""

import asyncio
from src.facedetector import viola_jones, mtcnn, ssd, yolo, retina_face, async_face_detctor
from src.common.libraries import *
from src.utils.utils import setup_logger, get_current_time

formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(funcName)s: %(message)s", "%d-%m-%Y %H:%M:%S")


def get_async_face_detector(video: Video):
    """Returns an instance of AsyncFaceDetector"""
    return async_face_detctor.AsyncFaceDetector(video)


async def detect_faces_in_realtime(detector, video: Video):
    log_file = f"{Config.LOGS_FOLDER_PATH}/face_detector.log"
    logger = setup_logger("FaceDetector", log_file, Config.LOG_LEVEL)

    video_input_filename = video.get_filename()
    out_filename = (
        "FaceDetector".lower()
        + "_"
        + Config.VIDEO_DETECTOR.lower()
        + "_"
        + get_current_time()
        + "."
        + Config.VIDEO_DEFAULT_FORMAT
    )
    video_output_filename = Config.VIDEO_OUTPUT_PATH / out_filename

    logger.info("Filename for input video: %s" % video_input_filename)
    logger.info("Filename for output video: %s" % video_output_filename)

    cap = None
    out = None
    write_to_file = os.path.exists(Config.VIDEO_OUTPUT_PATH)
    if write_to_file and os.path.exists(video_input_filename):
        cap = cv2.VideoCapture(str(video_input_filename))
        fourcc = cv2.VideoWriter_fourcc(*"X264")
        fourcc = cv2.VideoWriter_fourcc("m", "p", "4", "v")
        video_fps = (cap.get(cv2.CAP_PROP_FPS),)
        total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        logger.info(
            f"Frame Per second: {video_fps} \nTotal Frames: {total_frames} \n Height: {height} \nWidth: {width}"
        )
        out = cv2.VideoWriter(
            str(video_output_filename),
            apiPreference=0,
            fourcc=fourcc,
            fps=video_fps[0],
            frameSize=(int(width), int(height)),
        )
        logger.debug("Video is taken from input folder")
    else:  # this might not work properly
        cap = cv2.VideoCapture(0)
        logger.debug("Real time video capture started...")

    if not cap.isOpened():
        logger.error("Error opening video")
        raise FaceDetectionError("Error opening video")

    while cap.isOpened():
        ret, frame = cap.read()

        if not ret:
            logger.warning("Error reading frame")
            break

        faces = detector.detect_faces(frame)

        if len(faces) == 0:
            logger.debug("No faces detected")
        else:
            for face in faces:
                if detector.__class__.__name__ == "ViolaJones":
                    x, y, w, h = face
                else:
                    x, y, w, h = face["box"]
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        if write_to_file:
            out.write(frame)
        else:
            cv2.imshow("Video", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        await asyncio.sleep(0)

    if out:
        out.release()
    cap.release()
    cv2.destroyAllWindows()

    logger.debug("Face Detection is completed successfully")


def get_face_detector(detector_type):
    """
    This function is used to get the detector object based on the detector_type.
    It takes detector_type as input and returns the detector object

    Parameters:
    detector_type (str): type of detector. It should be one of the following
    ["ViolaJones", "MTCNN", "SSD", "YOLO", "RetinaFace"]

    Returns:
    object: detector object
    """
    if detector_type == "ViolaJones":
        return viola_jones.ViolaJones()
    elif detector_type == "MTCNN":
        return mtcnn.MTCNNDetector()
    elif detector_type == "SSD":
        return ssd.SSD()
    elif detector_type == "YOLO":
        raise NotImplementedError("Model is not implemented")
        # return yolo.YOLO()
    elif detector_type == "RetinaFace":
        raise NotImplementedError("Model is not implemented")
        # return retina_face.RetinaFace()
    else:
        raise ValueError(f"Invalid detector type: {detector_type}")
