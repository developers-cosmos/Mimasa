#!/usr/bin/env python3
"""
main.py

This module contains the main entry point for the program. It is responsible for
initializing all necessary components and executing the main logic of the program.
"""

from src.utils import utils

def main():
    """
    Main function
    """
    # Get the detector type from the user
    detector_type = input(
        "Enter the detector type (ViolaJones, MTCNN, SSD, YOLO, RetinaFace) (leave blank to select MTCNN): ") or "MTCNN"

    # Get an instance of the selected detector
    detector = utils.get_detector(detector_type)

    # Get the video filename from the user (if applicable)
    video_filename = input(
        "Enter the video filename (leave blank for webcam): ")

    # Start the face detection
    utils.detect_faces_in_realtime(detector, video_filename)


if __name__ == "__main__":
    main()
