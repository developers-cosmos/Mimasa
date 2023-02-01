#!/usr/bin/env python3
"""
This file contains utility functions that are commonly used throughout the application.
"""

from src.facedetector import viola_jones, mtcnn, ssd, yolo, retina_face
from src.common.libraries import *

def detect_faces_in_realtime(detector, video_filename=None):
    """
    This function is used to detect faces in real-time video feed.
    It takes the detector object and video filename as input.
    If video filename is not provided, it captures video feed from default camera.

    Parameters:
    detector (object): Face detection object, should be inherited from the FaceDetector ABC
    video_filename (str, optional): filename of the video file. Defaults to None.

    Returns:
    None
    """
    # Start the video capture
    cap = cv2.VideoCapture(0)
    if os.path.exists(video_filename):
        cap = cv2.VideoCapture(video_filename)

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
                x, y, w, h = face['box']
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

        # Display the frame
        cv2.imshow('Video', frame)

        # Exit the loop if the 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the video capture and close the window
    cap.release()
    cv2.destroyAllWindows()


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
