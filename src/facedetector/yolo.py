#!/usr/bin/env python3
"""
This module contains the YOLO class, which is a concrete implementation of the FaceDetector class,
using the YOLO object detection algorithm.

It takes in 3 parameters during initialization:
1. model_path: path to the pre-trained YOLO model
2. confidence: minimum probability required to consider a detection as a face
3. threshold: threshold for non-maxima suppression
"""

from src.facedetector.face_detector import FaceDetector
from src.common.libraries import *


class YOLO(FaceDetector):
    """
    Initializes the YOLO object detector and sets the necessary attributes.
    Parameters:
    model_path (str): The file path of the YOLO model.
    confidence (float): The minimum probability needed to filter out weak predictions.
    threshold (float): The threshold for non-maxima suppression to suppress weak,
                        overlapping bounding boxes.
    """

    def __init__(self, model_path, confidence, threshold):
        super().__init__()
        self.net = cv2.dnn.readNetFromDarknet(model_path, "cfg/yolov3.cfg")
        self.confidence = confidence
        self.threshold = threshold

    def detect_faces(self, frame):
        """
        Detects faces in a given frame using the YOLO object detector.
        Parameters:
            frame (numpy.ndarray): The input frame.
        Returns:
            numpy.ndarray: The input frame with rectangles drawn around the detected faces, and labels and confidence scores added.
        """
        (H, W) = frame.shape[:2]

        # construct a blob from the input frame and then perform a forward
        # pass of the YOLO object detector, giving us our bounding boxes and
        # associated probabilities
        blob = cv2.dnn.blobFromImage(
            frame, 1 / 255.0, (416, 16), swapRB=True, crop=False
        )
        self.net.setInput(blob)
        layer_outputs = self.net.forward(self.net.getUnconnectedOutLayersNames())

        boxes = []
        confidences = []
        classIDs = []

        # loop over each of the layer outputs
        for output in layer_outputs:
            # loop over each of the detections
            for detection in output:
                scores = detection[5:]
                classID = np.argmax(scores)
                confidence = scores[classID]

                # filter out weak predictions by ensuring the detected
                # probability is greater than the minimum probability
                if confidence > self.confidence:
                    box = detection[0:4] * np.array([W, H, W, H])
                    (centerX, centerY, width, height) = box.astype("int")

                    # use the center (x, y)-coordinates to derive the top and
                    # and left corner of the bounding box
                    x = int(centerX - (width / 2))
                    y = int(centerY - (height / 2))

                    # update our list of bounding box coordinates, confidences,
                    # and class IDs
                    boxes.append([x, y, int(width), int(height)])
                    confidences.append(float(confidence))
                    classIDs.append(classID)

        # apply non-maxima suppression to suppress weak, overlapping bounding
        # boxes
        idxs = cv2.dnn.NMSBoxes(boxes, confidences, self.confidence, self.threshold)

        # ensure at least one detection exists
        if len(idxs) > 0:
            # loop over the indexes we are keeping
            for i in idxs.flatten():
                # extract the bounding box coordinates
                (x, y) = (boxes[i][0], boxes[i][1])
                (w, h) = (boxes[i][2], boxes[i][3])

                # draw a rectangle around the face
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # add labels and confidence score
                label = f"Face: {classIDs[i]}"
                confidence_score = f"Confidence: {round(confidences[i], 2) * 100}%"
                cv2.putText(
                    frame,
                    label,
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    2,
                )
                cv2.putText(
                    frame,
                    confidence_score,
                    (x, y + h + 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    2,
                )

        return frame
