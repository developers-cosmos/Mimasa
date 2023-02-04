#!/usr/bin/env python3
import os
import cv2
import numpy as np
from gtts import gTTS
import tempfile
import subprocess
import moviepy.editor as mp
import dlib
from moviepy.editor import VideoFileClip

import librosa
import pydub
from pydub import AudioSegment


def change_language(audio: str, dest_lang: str) -> str:
    """
    This function converts the audio from a given language to another language.

    Parameters:
    audio_file (str): The path of the audio file.
    dest_lang (str): The language to which the audio is to be converted.

    Returns:
    str: The path of the converted audio file.
    """
    tts = gTTS(audio, lang=dest_lang)
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        tts.save(f.name)
    return tts


def translate_audio(audio_file, dest_lang):
    # Load the audio file
    y, sr = librosa.load(audio_file)

    # Extract speech segments using a voice activity detector (VAD)
    speech_segments = librosa.effects.split(y, top_db=30)

    # Extract music segments by subtracting the speech segments from the original audio
    music_segments = []
    start = 0
    for segment in speech_segments:
        end = segment[0]
        music_segments.append((start, end))
        start = segment[1]

    # Do something with the speech and music segments
    for speech_segment in speech_segments:
        y_speech = y[speech_segment[0] : speech_segment[1]]
        # do something with y_speech

    for music_segment in music_segments:
        y_music = y[music_segment[0] : music_segment[1]]

    # Load audio file
    sound = AudioSegment.from_file(audio_file)

    # Split audio into music and speech segments
    speech, music = y_speech, y_music

    # Use gTTS to translate speech segment
    tts = gTTS(text=speech, lang=dest_lang)
    speech_translated = ...  # code to get translated speech audio

    # Combine translated speech and music segments
    output = librosa.effects.overlay(speech_translated)

    # Save output to file
    output.export("output.mp3", format="mp3")
    librosa.output.write_wav("overlay.wav", output, sr)


def get_landmarks(frame):
    """
    Given an image of a face, detects facial landmarks and returns them as a list of points.
    :param frame: image of a face
    :return: list of facial landmarks
    """
    detector = dlib.get_frontal_face_detector()
    model_file = os.path.join(os.getcwd(), "data", "models", "shape_predictor_68_face_landmarks.dat")
    predictor = dlib.shape_predictor(model_file)

    # detect faces
    faces = detector(frame)

    # if no faces are detected, return an empty list
    if len(faces) == 0:
        return []

    # only consider the first face detected
    face = faces[0]
    landmarks = predictor(frame, face)

    return landmarks


def get_frames(video_file: str) -> list:
    """
    This function extracts frames from a given video.

    Parameters:
    video_file (str): The path of the video file.

    Returns:
    list: A list of numpy arrays representing each frame of the video.
    """
    # Open the input video file
    input_video = cv2.VideoCapture(video_file)
    # Get the frames per second (fps) and the frame dimensions of the video
    fps = int(input_video.get(cv2.CAP_PROP_FPS))
    frame_width = int(input_video.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(input_video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # Create an empty list to store the frames
    frames = []
    # Extract the frames from the input video
    while True:
        ret, frame = input_video.read()
        if not ret:
            break
        frames.append(frame)
    input_video.release()
    return frames, fps, frame_width, frame_height


def get_audio_from_video(video_file: str) -> str:
    """
    This function extracts audio from a given video file.

    Parameters:
    video_file (str): The path of the video file.

    Returns:
    str: The path of the audio file.
    """
    # with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
    #     subprocess.run(["ffmpeg", "-i", video_file, "-vn", "-acodec", "copy", f.name])
    # return f.name

    # create a video clip object
    clip = VideoFileClip(video_file)

    # extract audio
    audio = clip.audio

    # save audio to a file
    dest_path = os.path.join(os.getcwd(), "data", "videos", "audio.mp3")
    audio.write_audiofile(dest_path)
    return dest_path


def overlay_audio_on_video(audio_file, video_file):
    """
    This function overlays the audio from audio_file onto the video in video_file.

    Parameters:
        audio_file (str): The path to the audio file.
        video_file (str): The path to the video file.

    Returns:
        None
    """

    # Load the video and audio using moviepy
    video = mp.VideoFileClip(video_file)
    audio = mp.AudioFileClip(audio_file)

    # Overlay the audio on the video
    final_video = video.set_audio(audio)

    # Save the final video
    output_video_path = os.path.join(os.getcwd(), "data", "videos", "output2.mp4")
    final_video.write_videofile(output_video_path)


# Open the input video file
input_video_path = os.path.join(os.getcwd(), "data", "videos", "input.mp4")

# Get the audio from the video
audio = get_audio_from_video(input_video_path)

# Change the language of the audio
src_lang = "en"  # source language
dest_lang = "te-IN"  # destination language, hi-IN
changed_audio = change_audio_language(audio, dest_lang)

input_video = cv2.VideoCapture(input_video_path)

# Get the frames per second (fps) and the frame dimensions of the video
fps = int(input_video.get(cv2.CAP_PROP_FPS))
frame_width = int(input_video.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(input_video.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Get the frames from the video
frames, fps, frame_width, frame_height = get_frames(input_video_path)

output_video_path = os.path.join(os.getcwd(), "data", "videos", "output.mp4")
fourcc = cv2.VideoWriter_fourcc(*"XVID")
output_video = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))

# Map the aligned phoneme representation to the corresponding frames
# and apply the appropriate facial expressions and mouth movements to each frame
for i, frame in enumerate(frames):
    # Apply facial expressions and mouth movements to the frame
    landmarks = get_landmarks(frame)

    # if no faces are detected, continue to next frame
    if len(landmarks.parts()) == 0:
        continue
    mouth_landmarks = landmarks.parts()[48:68]
    for j, point in enumerate(mouth_landmarks):
        cv2.circle(frame, (point.x, point.y), 2, (255, 0, 0), -1)

    # Write the frame to the output video
    if not output_video.write(frame):
        print("error in writing frame")
        break

# Release the output video
output_video.release()

# Overlay the changed audio over the output video
overlay_audio_on_video(changed_audio, output_video_path)
