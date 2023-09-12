#!/usr/bin/env python3
"""
This module contains the FaceDetector class, which is an abstract base class
for different face detection algorithms.
"""


class FaceDetector:
    """
    This class is responsible for detecting faces in an image or video frame.
    """

    def detect_faces(self, frame):
        """
        Detect faces in the given frame.

        Args:
            frame (numpy.ndarray): The image or video frame in which faces need to be detected.

        Returns:
            list: A list of bounding boxes for the detected faces.
        """
        raise NotImplementedError
