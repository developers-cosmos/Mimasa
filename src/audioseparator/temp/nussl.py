import nussl
import torch

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
audio_signal = nussl.AudioSignal(
    r"C:\Users\ryellenki\~R\practice\mimasa-project\Mimasa\mimasa\data\audios\input.wav",
    sample_rate=44100,
)

separator = nussl.separation.deep.DeepMaskEstimation(
    nussl.AudioSignal(),
    model_path="checkpoints/best.model.pth",
    device=DEVICE,
)

separator.audio_signal = audio_signal
estimates = separator()
estimates = {"vocals": estimates[0], "bass+drums+other": audio_signal - estimates[0]}

speech_siganl = estimates["vocals"]
speech_siganl.write_audio_to_file("vocals.wav")

music_signal = estimates["bass+drums+other"]
music_signal.write_audio_to_file("music.wav")

from pydub import AudioSegment

# Load the two audio files
audio1 = AudioSegment.from_wav("music.wav")
audio2 = AudioSegment.from_wav("vocals.wav")

# Invert the audio file that you want to remove
audio2_inverted = audio2.invert_phase()

# Mix the first audio file with the inverted second audio file
result = audio1.overlay(audio2_inverted)

# Save the resulting audio file
result.export("result.wav", format="wav")
