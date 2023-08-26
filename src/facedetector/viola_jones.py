#!/usr/bin/env python3
"""
This module contains the ViolaJones class, which is a concrete implementation
of the FaceDetector class.
"""

from src.facedetector.face_detector import FaceDetector
from src.common.libraries import *


class ViolaJones(FaceDetector):
    """
    ViolaJones class is a subclass of FaceDetector. It uses Viola-Jones algorithm
    to detect faces in an image.
    """

    def __init__(self):
        """
        Initializes the classifier with the path to the classifier xml file.
        """
        self.classifier = cv2.CascadeClassifier("data/models/classifiers/haarcascade_frontalface_default.xml")

    def detect_faces(self, frame):
        """
        detect_faces method takes an image as input and returns the coordinates of
        the bounding boxes around the detected faces.
        """
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.classifier.detectMultiScale(gray_frame, 1.3, 5)
        return faces
