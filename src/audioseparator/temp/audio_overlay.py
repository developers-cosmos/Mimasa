import os
import librosa
import numpy as np
from gtts import gTTS
from pydub import AudioSegment

# Load the audio file
audio_file = os.path.join(os.getcwd(), "data", "videos", "audio.mp3")
audio, sr = librosa.load(audio_file)

# Perform STFT on the audio file
stft = librosa.stft(audio)

# Compute the magnitude spectrogram
magnitude_spectrogram = np.abs(stft)

# Compute the energy of each frame
frame_energy = np.sum(magnitude_spectrogram**2, axis=0)

# Identify the frames that correspond to speech
speech_frames = np.where(frame_energy > np.mean(frame_energy))

# Identify the frames that correspond to music
music_frames = np.where(frame_energy <= np.mean(frame_energy))

# Extract the speech and music segments
speech_segment = librosa.istft(stft[:, np.ix_(speech_frames)])
music_segment = librosa.istft(stft[:, np.ix_(music_frames)])

# Translate the speech using gTTS
tts = gTTS("Hello, I am changing the language", lang="fr")
tts.save(os.path.join(os.getcwd(), "data", "videos", "output_speech.mp3"))

# Load the new speech audio
new_speech_audio = AudioSegment.from_file(
    os.path.join(os.getcwd(), "data", "videos", "output_speech.mp3")
)

# Convert the music segment to an audio file
librosa.output.write_wav(
    os.path.join(os.getcwd(), "data", "videos", "music.wav"), music_segment, sr
)

# Load the music segment
music_audio = AudioSegment.from_file(
    os.path.join(os.getcwd(), "data", "videos", "music.wav")
)

# Overlay the new speech on top of the original music
result = music_audio.overlay(new_speech_audio)

# Save the resulting audio file
result.export(os.path.join(os.getcwd(), "data", "videos", "output.mp3"), format="mp3")
