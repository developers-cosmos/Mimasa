#!/usr/bin/env python3
"""
This module contains the RetinaFace class, which is a concrete implementation of the
FaceDetector class.
"""

from src.common.libraries import *
from src.facedetector.face_detector import FaceDetector


class RetinaFace(FaceDetector):
    """
    This class is responsible for detecting faces in an image or video frame using
    RetinaFace Algorithm.
    """

    def __init__(self, model_path):
        """
        Initialize the class and set the model path
        """
        self.net = cv2.dnn.readNet(model_path)

    def detect_faces(self, frame):
        """
        Detect faces in the given frame using RetinaFace

        Parameters:
        - frame (numpy array): The frame in which faces need to be detected

        Returns:
        - None
        """
        (H, W) = frame.shape[:2]

        # construct a blob from the input frame and then perform a forward
        # pass of the RetinaFace object detector, giving us our bounding boxes and
        # associated probabilities
        blob = cv2.dnn.blobFromImage(frame, 1.0, (W, H), (104.0, 177.0, 123.0))
        self.net.setInput(blob)
        detections = self.net.forward()

        boxes = []
        confidences = []
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > 0.8:
                box = detections[0, 0, i, 3:7] * np.array([W, H, W, H])
                (startX, startY, endX, endY) = box.astype("int")

                # update our list of bounding box coordinates, confidences
                boxes.append([startX, startY, endX, endY])
                confidences.append(confidence)

        # apply non-maxima suppression to suppress weak, overlapping bounding
        # boxes
        idxs = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.3)

        # ensure at least one detection exists
        if len(idxs) > 0:
            # loop over the indexes we are keeping
            for i in idxs.flatten():
                # extract the bounding box coordinates
                (x, y) = (boxes[i][0], boxes[i][1])
                (w, h) = (boxes[i][2], boxes[i][3])

                # draw a rectangle around the face
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
