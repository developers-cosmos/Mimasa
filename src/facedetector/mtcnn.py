#!/usr/bin/env python3
"""
This module contains the MTCNNDetector class, which is a concrete implementation of the FaceDetector class.
"""

from mtcnn import MTCNN
from src.facedetector.face_detector import FaceDetector
from src.common.libraries import *


class MTCNNDetector(FaceDetector):
    """
    This class is responsible for detecting faces in an image or video frame using MTCNN Algorithm.
    """

    def __init__(self):
        """
        Initialize the class and call the parent class constructor
        """
        super().__init__()
        self.detector = MTCNN()

    def detect_faces(self, frame):
        """
        Detect faces in the given frame using MTCNN

        Parameters:
        - frame (numpy array): The frame in which faces need to be detected

        Returns:
        - faces (List[Dict]): List of dictionaries containing the coordinates of the detected faces
        """
        faces = self.detector.detect_faces(frame)
        return faces
