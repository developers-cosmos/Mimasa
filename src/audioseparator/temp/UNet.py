import os
import numpy as np
import librosa
import torch
from flerken.models import UNet
from collections import OrderedDict
import soundfile as sf
import logging
import torch.nn.functional as F

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s: %(message)s")

ORIGINAL_SAMPLING_RATE = 44100
TARGET_SAMPLING_RATE = 10880
DURATION = 6
NFFT = 1022
HOP_LENGTH = 256
STFT_WIDTH = int((TARGET_SAMPLING_RATE * DURATION / HOP_LENGTH) + 1)
K = 2
BATCH_SIZE = 16
ENERGY_THRESHOLD = 0
SOURCES = ["vocals", "accompaniment"]
SOURCES_SUBSET = ["vocals", "accompaniment"]
AUDIO_BASE_DIR = os.path.join(os.getcwd(), "data", "audios")

weights_path = os.path.join(os.getcwd(), "data", "models", "weights", "UNet", "bestcheckpoint_2.pth")


def warpgrid(bs, h, w, warp=True):
    # meshgrid
    x = np.linspace(-1, 1, w)
    y = np.linspace(-1, 1, h)
    xv, yv = np.meshgrid(x, y)
    grid = np.zeros((bs, h, w, 2))
    grid_x = xv
    if warp:
        grid_y = (np.power(21, (yv + 1) / 2) - 11) / 10
    else:
        grid_y = np.log(yv * 10 + 11) / np.log(21) * 2 - 1
    grid[:, :, :, 0] = grid_x
    grid[:, :, :, 1] = grid_y
    grid = grid.astype(np.float32)
    return grid


class Wrapper(torch.nn.Module):
    def __init__(self, model, main_device="cpu"):
        super(Wrapper, self).__init__()
        self.L = len(SOURCES_SUBSET)
        self.model = model
        self.main_device = main_device
        self.grid_warp = torch.from_numpy(warpgrid(BATCH_SIZE, 256, STFT_WIDTH, warp=True)).float()

    def forward(self, x):
        if x.shape[0] == BATCH_SIZE:
            mags = F.grid_sample(x, self.grid_warp)
        else:  # for the last batch, where the number of samples are generally lesser than the batch_size
            custom_grid_warp = torch.from_numpy(warpgrid(x.shape[0], 256, STFT_WIDTH, warp=True)).float()
            mags = F.grid_sample(x, custom_grid_warp)

        # gt_masks = torch.div(mags[:, :-1], mags[:, -1].unsqueeze(1).expand(x.shape[0], self.L, *mags.shape[2:]))
        # gt_masks.clamp_(0., 10.)

        log_mags = torch.log(mags[:, -1].unsqueeze(1)).detach()
        gt_mags = x[:, :-1]
        mix_mag = x[:, -1].unsqueeze(1)
        pred_masks = self.model(log_mags)
        pred_masks = torch.relu(pred_masks)
        mag_mix_sq = mags[:, -1].unsqueeze(1)
        pred_mags_sq = pred_masks * mag_mix_sq
        # gt_mags_sq = gt_masks * mag_mix_sq

        network_output = [
            None,
            pred_mags_sq,
            gt_mags,
            mix_mag,
            None,
            pred_masks,
        ]  # BxKx256x256, BxKx256x256, BxKx512x256, Bx1x512x256, BxKx256x256, BxKx256x256
        return network_output


class AudioUNet(torch.nn.Module):
    def __init__(self):
        super(AudioUNet, self).__init__()
        self.unet = UNet([32, 64, 128, 256, 512, 1024, 2048], K=2, useBN=True)

    def forward(self, x):
        return self.unet(x)


def load_model(weights_path):
    """Load the audio separation model"""
    logging.info("Loading the audio separation model")
    model = AudioUNet()
    state_dict = torch.load(weights_path, map_location=torch.device("cpu"))
    state_dict = state_dict["state_dict"]
    new_state_dict = OrderedDict()
    for k, v in state_dict.items():
        name = k.replace("model.", "unet.")
        new_state_dict[name] = v
    model.load_state_dict(new_state_dict, strict=True)
    model = Wrapper(model)
    logging.info("Model Loaded Successfully")
    return model


def istft_reconstruction(mag, phase, hop_length=256):
    """
    Perform the inverse STFT to convert the magnitude and phase to audio signals

    Parameters:
    mag (np.ndarray): magnitude of the STFT
    phase (np.ndarray): phase of the STFT
    hop_length (int): the Hop Length parameter for ISTFT

    Returns:
    wav (np.ndarray): audio signal
    """
    logging.info("Performing ISTFT reconstruction")
    spec = mag.astype(complex) * np.exp(1j * phase)
    wav = librosa.istft(spec, hop_length=hop_length)
    logging.info("ISTFT reconstruction completed")
    return np.clip(wav, -1.0, 1.0)


def preprocess_audio(
    audio_file,
    original_sr=ORIGINAL_SAMPLING_RATE,
    target_sr=TARGET_SAMPLING_RATE,
    duration=DURATION,
    nfft=NFFT,
    hop_length=HOP_LENGTH,
):
    """Load, Downsample and extract STFT features from the audio file"""
    logging.info("Preprocessing audio")
    audio, sr = librosa.load(audio_file, sr=original_sr)
    audio = librosa.resample(audio, orig_sr=sr, target_sr=target_sr)
    logging.info("Audio processing is completed")
    return audio


def _stft(sources):
    s = torch.from_numpy(sources).float()
    shape = s.size()
    with torch.no_grad():
        stft_output = torch.stft(
            s.view(-1, shape[-1]),
            n_fft=NFFT,
            hop_length=HOP_LENGTH,
            window=torch.hann_window(NFFT),
        )
        stft = stft_output.view(*shape[:-1], *stft_output.size()[1:3], 2).data.cpu().numpy()
    stft = stft[..., 0] + stft[..., 1] * 1j
    return stft


def create_folder(path):
    if not os.path.exists(path):
        os.umask(0)  # To mask the permission restrictions on new files/directories being create
        os.makedirs(path, 0o755)  # setting permissions for the folder


def get_signal_energy(signal):
    return sum(abs(signal) ** 2)


def save_chunks(chunk_id, subset_type, track_name, sources, energy_profile):
    save_folder_path = os.path.join(AUDIO_BASE_DIR, subset_type, track_name, str(chunk_id))
    create_folder(save_folder_path)
    true_label = np.zeros(len(SOURCES) + 1, dtype="int")
    for source_id, source in enumerate([*SOURCES, "MIX"]):
        signal = sources[source_id, chunk_id]
        signal_energy = get_signal_energy(signal)
        if int(signal_energy) > ENERGY_THRESHOLD:
            true_label[source_id] = 1
        save_path = os.path.join(save_folder_path, source + "_" + str(int(round(signal_energy))) + ".wav")
        energy_profile[source_id][os.path.dirname(save_path)] = signal_energy
        librosa.output.write_wav(save_path, signal, TARGET_SAMPLING_RATE)
    return energy_profile, true_label[:-1]


def get_stft(audio, NFFT=1022, HOP_LENGTH=256):
    """
    Compute the STFT features of the audio signal

    Parameters:
    audio (np.ndarray): audio signal
    NFFT (int): the NFFT parameter for STFT
    HOP_LENGTH (int): the Hop Length parameter for STFT

    Returns:
    stft (torch.tensor): STFT features of the audio
    """
    logging.info("Performing fourier transform on the audio")
    sources = np.stack(audio)
    stft_output = _stft(sources)

    print(stft_output)

    # window = int(TARGET_SAMPLING_RATE * DURATION)
    # M = (np.max(sources.shape) // window)

    # zero_padding = window - np.max(sources.shape) % window
    # splits = np.concatenate([sources, np.zeros([len(SOURCES) + 1, zero_padding])], axis=1)
    # sources_split = np.reshape(splits, splits.shape[:-1] + (M + 1, window))

    # energy_profile = [{} for _ in range(len(SOURCES) + 1)]
    # sample_dict = {}
    # for chunk_id in range(stft_output.shape[1]):
    #     matrix = stft_output[:, chunk_id, ...]
    #     energy_profile, true_label = save_chunks(chunk_id, 'test', 'music', sources_split, energy_profile)
    #     sample_dict['spec'] = matrix
    #     sample_dict['true_label'] = true_label
    #     full_path = os.path.join(AUDIO_BASE_DIR, str(chunk_id))
    #     np.save(full_path, sample_dict)
    #     print('[{0}/{1}] || [{2}||{3}]'.format(chunk_id + 1, stft_output.shape[1], 'track_id' + 1, len(['tracks'])))
    # del sources_split

    # stft = librosa.core.stft(audio, n_fft=NFFT, hop_length=HOP_LENGTH)

    stft = stft_output
    stft = np.absolute(stft)
    # stft = np.log1p(stft)
    stft = stft[np.newaxis, np.newaxis, :, :]
    print(stft.shape)
    # stft = stft.transpose(0, 1, 2, 3)
    stft = torch.from_numpy(stft).float()
    logging.info("Fourier transform on audio is completed")
    return stft


def source_separation(model, stft, HOP_LENGTH=256, TARGET_SAMPLING_RATE=10880):
    """
    Perform source separation and return the speech and music signals

    Parameters:
    model (torch.nn.Module): PyTorch model to perform source separation
    stft (torch.tensor): STFT features of the audio
    HOP_LENGTH (int): the Hop Length parameter for ISTFT
    TARGET_SAMPLING_RATE (int): target sample rate

    Returns:
    speech_signal (torch.tensor): speech audio signal
    music_signal (torch.tensor): music audio signal
    """
    logging.info("Performing source separation")

    # tensor = model(stft)
    # tensor = tensor.detach().numpy()
    # tensor = np.transpose(tensor, (0, 2, 1, 3))
    # tensor = np.squeeze(tensor)
    # speech_signal = torch.from_numpy(istft_reconstruction(tensor[0], np.zeros_like(tensor[0]), HOP_LENGTH))
    # music_signal = torch.from_numpy(istft_reconstruction(tensor[1], np.zeros_like(tensor[1]), HOP_LENGTH))

    _, _, gt_mags, _, _, pred_masks = model(stft)

    gt_mags = gt_mags.detach().numpy()
    pred_masks = pred_masks.detach().numpy()

    print(pred_masks)
    pred_audio = torch.from_numpy(istft_reconstruction(pred_masks[0], np.zeros_like(pred_masks[0]), HOP_LENGTH))

    pred_audio = pred_audio.detach().numpy()

    sf.write(
        os.path.join(os.getcwd(), "data", "videos", "speech.wav"),
        pred_audio[0],
        samplerate=TARGET_SAMPLING_RATE,
    )

    input()
    logging.info("Returning speech signal and music signal")
    return


def main():
    """
    Main function
    """
    model = load_model(weights_path)

    audio_file = os.path.join(os.getcwd(), "data", "videos", "mix.wav")
    processed_audio = preprocess_audio(audio_file)
    stft = get_stft(processed_audio)

    audio, sr = librosa.load(audio_file, sr=ORIGINAL_SAMPLING_RATE)
    source_separation(model, stft)
    # sf.write(os.path.join(os.getcwd(), "data", "videos", "speech.wav"), speech_signal.detach().numpy(), samplerate=TARGET_SAMPLING_RATE)
    # sf.write(os.path.join(os.getcwd(), "data", "videos", "music.wav"), music_signal.detach().numpy(), samplerate=TARGET_SAMPLING_RATE)


if __name__ == "__main__":
    main()
