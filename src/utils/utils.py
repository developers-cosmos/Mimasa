#!/usr/bin/env python3
"""
This file contains utility functions that are commonly used throughout the application.
"""

from src.facedetector import viola_jones, mtcnn, ssd, yolo, retina_face
from src.audioseparator import nussl_separator
from src.common.libraries import *
from src.common.config import Config
from src.common.video import Video
from src.common.exceptions import FaceDetectionError

logging.basicConfig(level=Config.LOG_LEVEL, format="%(asctime)s [%(levelname)s]: %(message)s")


def get_current_time() -> str:
    """Returns the current time"""

    # get the current time
    current_time = datetime.datetime.now()

    # format the time as a string
    time_str = current_time.strftime("%Y-%m-%d_%H-%M-%S")
    return time_str


def detect_faces_in_realtime(detector, video: Video):
    """
    This function is used to detect faces in real-time video feed.
    It takes the detector object and video filename as input.
    If video filename is not provided, it captures video feed from default camera.

    Parameters:
    detector (object): Face detection object, should be inherited from the FaceDetector ABC
    video_input_filename (str, optional): filename of the video file. Defaults to None.

    Returns:
    None
    """
    video_input_filename = video.get_filename()
    print(type(video_input_filename))

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

    logging.info("Filename for input video: %s" % video_input_filename)
    logging.info("Filename for output video: %s" % video_output_filename)

    cap = None
    write_to_file = os.path.exists(Config.VIDEO_OUTPUT_PATH)
    if write_to_file and os.path.exists(video_input_filename):
        cap = cv2.VideoCapture(str(video_input_filename))
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        out = cv2.VideoWriter(str(video_output_filename), fourcc, 20.0, (640, 480))
        logging.debug("Video is taken from input folder")
    else:
        cap = cv2.VideoCapture(0)
        logging.debug("Real time video capture started...")

    if not cap.isOpened():
        logging.error("Error opening video")
        raise FaceDetectionError("Error opening video")

    while True:
        # Read a frame from the video
        ret, frame = cap.read()

        # Detect faces in the frame
        faces = detector.detect_faces(frame)

        # Draw a rectangle around the detected faces
        for face in faces:
            if detector.__class__.__name__ == "ViolaJones":
                x, y, w, h = face
            else:
                x, y, w, h = face["box"]
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        if write_to_file:
            # Write the frame to the output file
            out.write(frame)
        else:
            # Display the frame
            cv2.imshow("Video", frame)

            # Exit the loop if the 'q' key is pressed
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    # Release the video capture and close the window
    cap.release()
    cv2.destroyAllWindows()

    logging.debug("Face Detection is completed successfully")


def get_detector(detector_type):
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


def get_audio_separator(separator_type: str = None, model_path: str = None):
    """
    This function is used to get the AudioSeparator object based on the separator_type.

    Parameters:
    separator_type (str): type of separator. It should be one of the following
    ["NUSSL"]

    Returns:
    object: separator object
    """
    if separator_type == "NUSSL":
        return nussl_separator.NUSSL(model_path)
    else:
        raise ValueError(f"Invalid separator type: {separator_type}")
