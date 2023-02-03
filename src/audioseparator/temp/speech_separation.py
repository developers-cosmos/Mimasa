import os
import librosa
import numpy as np
import nussl


AUDIO_BASE_DIR = os.path.join(os.getcwd(), "data", "audios")

audio_src_file = os.path.join(AUDIO_BASE_DIR, "input.wav")
speech_filepath = os.path.join(AUDIO_BASE_DIR, "speech.wav")
music_filepath = os.path.join(AUDIO_BASE_DIR, "music.wav")

# Load audio file
audio_signal = nussl.AudioSignal(audio_src_file, sample_rate=44100)

print("Duration: {} seconds".format(audio_signal.signal_duration))
print("Duration in samples: {} samples".format(audio_signal.signal_length))
print("Number of channels: {} channels".format(audio_signal.num_channels))
print("File name: {}".format(audio_signal.file_name))
print("Full path to input: {}".format(audio_signal.path_to_input_file))
print("Root mean square energy: {:.4f}".format(audio_signal.rms().mean()))

# model_path = nussl.efz_utils.download_trained_model(
#     'mask-inference-wsj2mix-model-v1.pth')

# Define configuration
stft_params = {"fft_size": 2048, "hop_size": 512, "win_size": 2048}

config = {
    "stft_params": stft_params,
    "sample_rate": 44100,
}


class MyHPSS(nussl.separation.base.MaskSeparationBase):
    def __init__(
        self, audio_signal, kernel_size=31, mask_type="soft", mask_threshold=0.5
    ):
        """Setup code goes here."""

        # The super class will save all of these attributes for us.
        super().__init__(
            input_audio_signal=audio_signal,
            mask_type=mask_type,
            mask_threshold=mask_threshold,
        )

        # Save the kernel size.
        self.kernel_size = kernel_size

    def run(self):
        """Code for running HPSS. Returns masks."""

        # Keep a list of each mask type.
        harmonic_masks = []
        percussive_masks = []

        # Our signal might have more than one channel:
        # Apply HPSS to each channel individually.
        for ch in range(self.audio_signal.num_channels):
            # apply mask
            harmonic_mask, percussive_mask = librosa.decompose.hpss(
                self.stft[:, :, ch], kernel_size=self.kernel_size, mask=True
            )
            harmonic_masks.append(harmonic_mask)
            percussive_masks.append(percussive_mask)

        # Order the masks correctly.
        harmonic_masks = np.stack(harmonic_masks, axis=-1)
        percussive_masks = np.stack(percussive_masks, axis=-1)
        _masks = np.stack([harmonic_masks, percussive_masks], axis=-1)

        # Convert the masks to `nussl.MaskBase` types.
        self.result_masks = []
        for i in range(_masks.shape[-1]):
            mask_data = _masks[..., i]
            if self.mask_type == self.MASKS["binary"]:
                mask_data = _masks[..., i] == np.max(_masks, axis=-1)
            mask = self.mask_type(mask_data)
            self.result_masks.append(mask)

        # Return the masks>
        return self.result_masks


separator = MyHPSS(audio_signal=audio_signal)
sources = separator()

estimated_signals = separator.make_audio_signals()

speech_siganl = estimated_signals[0]
speech_siganl.write_audio_to_file(speech_filepath)

music_signal = estimated_signals[1]
music_signal.write_audio_to_file(music_signal)


# Perform source separation using the Spectral Masking based method
# config = nussl.AudioSignal.SpectrogramConfig(sample_rate=44100, n_fft=2048, hop_length=512)
# separator = nussl.separation.deep.DeepMaskEstimation(input_audio_signal=audio_signal)

# masks = separator.forward(**config)

# sources = separator.run(masks=masks)

# Get the separated audio signals for speech and music
# speech_signal = sources[0]
# music_signal = separator.make_audio_signal(component='accompaniment')

# # Write the separated signals to separate audio files
# speech_signal.write_audio_to_file(speech_filepath)
# music_signal.write_audio_to_file('path/to/music_file.wav')

# # Save separated audio files
# sf.write(speech_filepath, speech, samplerate=sr)
# sf.write(music_filepath, music, samplerate=sr)
