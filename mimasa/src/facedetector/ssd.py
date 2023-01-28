#!/usr/bin/env python3
"""
This module contains the SSD class, which is a concrete implementation
of the FaceDetector class.
"""

from src.facedetector.face_detector import FaceDetector
from src.common.libraries import *

class SSD(FaceDetector):
    """
    This class is responsible for detecting faces in an image or video frame using SSD Algorithm.
    """
    def init(self):
        """
        Initialize the class by loading the pre-trained model
        """
        super().__init__()
        self.detector = cv2.dnn.readNetFromCaffe(
            "path/to/model.prototxt", "path/to/weights.caffemodel")

    def detect_faces(self, frame):
        """
        Detect faces in the given frame using the pre-trained model
        :param frame: The frame in which faces need to be detected
        :return: List of tuples containing the coordinates of the detected faces in the format (x, y, width, height)
        """
        (h, w) = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(
            frame, 1.0, (300, 300), (104.0, 177.0, 123.0))
        self.detector.setInput(blob)
        detections = self.detector.forward()
        faces = []
        for i in range(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > 0.5:
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")
                faces.append((startX, startY, endX-startX, endY-startY))
