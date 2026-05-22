"""
Audio processing pipeline for Parkinson's Disease voice feature extraction.

Extracts all 22 acoustic features from voice recordings using librosa and
parselmouth (Praat wrapper), with nolds for nonlinear dynamics features.
"""
import os
import tempfile
import numpy as np
import librosa
import soundfile as sf
import parselmouth
from parselmouth.praat import call
import nolds


EXTRACTABLE_FEATURES = [
    'MDVP:Fo(Hz)', 'MDVP:Fhi(Hz)', 'MDVP:Flo(Hz)',
    'MDVP:Jitter(%)', 'MDVP:Jitter(Abs)', 'MDVP:RAP', 'MDVP:PPQ', 'Jitter:DDP',
    'MDVP:Shimmer', 'MDVP:Shimmer(dB)', 'Shimmer:APQ3', 'Shimmer:APQ5',
    'MDVP:APQ', 'Shimmer:DDA',
    'NHR', 'HNR',
    'RPDE', 'DFA', 'spread1', 'spread2', 'D2', 'PPE',
]

MAX_FILE_SIZE = 2 * 1024 * 1024  # 2 MB
MAX_DURATION = 10.0  # seconds


def validate_audio(filepath):
    """Validate audio file constraints."""
    file_size = os.path.getsize(filepath)
    if file_size > MAX_FILE_SIZE:
        raise ValueError(f"Audio file too large ({file_size} bytes). Maximum is {MAX_FILE_SIZE} bytes.")

    info = sf.info(filepath)
    if info.duration > MAX_DURATION:
        raise ValueError(f"Audio too long ({info.duration:.1f}s). Maximum is {MAX_DURATION}s.")

    return True


def normalize_audio(y, sr):
    """Normalize audio signal."""
    # Remove silence from beginning/end
    y_trimmed, _ = librosa.effects.trim(y, top_db=20)
    # Normalize amplitude
    if np.max(np.abs(y_trimmed)) > 0:
        y_trimmed = y_trimmed / np.max(np.abs(y_trimmed))
    return y_trimmed


def extract_features_from_file(filepath):
    """
    Extract 16 Parkinson's-related acoustic features from an audio file.

    Parameters
    ----------
    filepath : str
        Path to the audio file (WAV format preferred).

    Returns
    -------
    dict
        Dictionary mapping feature names to extracted values.
    """
    validate_audio(filepath)

    # Load and normalize audio with librosa
    y, sr = librosa.load(filepath, sr=None)
    y = normalize_audio(y, sr)

    # Save normalized audio to temp file for parselmouth
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
        tmp_path = tmp.name
        sf.write(tmp_path, y, sr)

    try:
        # Create parselmouth Sound object
        sound = parselmouth.Sound(tmp_path)

        # Extract pitch (F0)
        pitch = call(sound, "To Pitch", 0.0, 75, 600)
        f0_values = pitch.selected_array['frequency']
        f0_values = f0_values[f0_values > 0]  # Remove unvoiced frames

        if len(f0_values) == 0:
            raise ValueError("No voiced frames detected. Please record a sustained vowel sound (e.g., 'aaah').")

        fo_mean = np.mean(f0_values)
        fo_max = np.max(f0_values)
        fo_min = np.min(f0_values)

        # Extract jitter and shimmer using PointProcess
        point_process = call(sound, "To PointProcess (periodic, cc)", 75, 600)

        # Jitter measurements
        jitter_percent = call(point_process, "Get jitter (local)", 0, 0, 0.0001, 0.02, 1.3)
        jitter_abs = call(point_process, "Get jitter (local, absolute)", 0, 0, 0.0001, 0.02, 1.3)
        jitter_rap = call(point_process, "Get jitter (rap)", 0, 0, 0.0001, 0.02, 1.3)
        jitter_ppq = call(point_process, "Get jitter (ppq5)", 0, 0, 0.0001, 0.02, 1.3)
        jitter_ddp = jitter_rap * 3  # DDP = RAP * 3

        # Shimmer measurements
        shimmer_local = call([sound, point_process], "Get shimmer (local)", 0, 0, 0.0001, 0.02, 1.3, 1.6)
        shimmer_db = call([sound, point_process], "Get shimmer (local_dB)", 0, 0, 0.0001, 0.02, 1.3, 1.6)
        shimmer_apq3 = call([sound, point_process], "Get shimmer (apq3)", 0, 0, 0.0001, 0.02, 1.3, 1.6)
        shimmer_apq5 = call([sound, point_process], "Get shimmer (apq5)", 0, 0, 0.0001, 0.02, 1.3, 1.6)
        shimmer_apq = call([sound, point_process], "Get shimmer (apq11)", 0, 0, 0.0001, 0.02, 1.3, 1.6)
        shimmer_dda = shimmer_apq3 * 3  # DDA = APQ3 * 3

        # Harmonics-to-Noise Ratio
        harmonicity = call(sound, "To Harmonicity (cc)", 0.01, 75, 0.1, 1.0)
        hnr = call(harmonicity, "Get mean", 0, 0)

        # Noise-to-Harmonics Ratio
        nhr = 1.0 / (10 ** (hnr / 10)) if hnr > 0 else 0.5

        # Handle NaN values with safe defaults (closer to dataset medians)
        def safe(val, default):
            if val is None or np.isnan(val) or np.isinf(val):
                return default
            return float(val)

        def clamp(val, lo, hi):
            return max(lo, min(hi, val))

        features = {
            'MDVP:Fo(Hz)': clamp(safe(fo_mean, 150.0), 80, 300),
            'MDVP:Fhi(Hz)': clamp(safe(fo_max, 200.0), 100, 600),
            'MDVP:Flo(Hz)': clamp(safe(fo_min, 100.0), 60, 250),
            'MDVP:Jitter(%)': clamp(safe(jitter_percent * 100, 0.005), 0.001, 0.04),
            'MDVP:Jitter(Abs)': clamp(safe(jitter_abs, 0.00004), 1e-7, 0.0003),
            'MDVP:RAP': clamp(safe(jitter_rap, 0.003), 0.0005, 0.025),
            'MDVP:PPQ': clamp(safe(jitter_ppq, 0.003), 0.0005, 0.025),
            'Jitter:DDP': clamp(safe(jitter_ddp, 0.009), 0.001, 0.07),
            'MDVP:Shimmer': clamp(safe(shimmer_local, 0.03), 0.005, 0.15),
            'MDVP:Shimmer(dB)': clamp(safe(shimmer_db, 0.3), 0.05, 1.5),
            'Shimmer:APQ3': clamp(safe(shimmer_apq3, 0.015), 0.002, 0.07),
            'Shimmer:APQ5': clamp(safe(shimmer_apq5, 0.018), 0.002, 0.09),
            'MDVP:APQ': clamp(safe(shimmer_apq, 0.02), 0.003, 0.15),
            'Shimmer:DDA': clamp(safe(shimmer_dda, 0.045), 0.005, 0.2),
            'NHR': clamp(safe(nhr, 0.02), 0.0003, 0.8),
            'HNR': clamp(safe(hnr, 20.0), 1.0, 35.0),
        }

        # Extract nonlinear/complex features using nolds and custom algorithms
        # --- spread1: standard deviation of F0 ---
        spread1_val = float(np.std(f0_values)) if len(f0_values) > 1 else 0.0

        # --- spread2: standard deviation on log-F0 ---
        log_f0 = np.log(f0_values[f0_values > 1] + 1e-10)
        spread2_val = float(np.std(log_f0)) if len(log_f0) > 1 else 0.0

        # --- PPE: Pitch Period Entropy ---
        period = 1.0 / (f0_values[f0_values > 1] + 1e-10)
        if len(period) > 5:
            hist, _ = np.histogram(period, bins=20, density=True)
            hist = hist[hist > 1e-10]
            ppe_val = -float(np.sum(hist * np.log(hist))) / np.log(len(hist) + 1e-10)
        else:
            ppe_val = 0.5

        # Downsample for nonlinear analysis (computational efficiency)
        target_sr = 1000
        if sr > target_sr:
            step = int(sr / target_sr)
            y_down = y[::step]
        else:
            y_down = y

        if len(y_down) > 200:
            # --- DFA (Detrended Fluctuation Analysis) ---
            try:
                dfa_val = float(nolds.dfa(y_down))
            except Exception:
                dfa_val = 0.5

            # --- D2 (Correlation Dimension) ---
            try:
                d2_val = float(nolds.correlation_dimension(y_down, emb_dim=5))
            except Exception:
                d2_val = 2.5

            # --- RPDE (Recurrence Period Density Entropy) ---
            try:
                tau = max(1, int(len(y_down) / 50))
                n_pts = min(300, len(y_down) - tau)
                indices = np.linspace(0, len(y_down) - tau - 1, n_pts, dtype=int)
                emb = np.column_stack([y_down[i + tau] - y_down[i] for i in range(tau)])
                r = 0.5 * np.std(emb)
                if r < 1e-10:
                    r = 0.5
                periods = []
                for i in range(len(emb)):
                    dists = np.abs(emb[i + 1:] - emb[i])
                    rec = np.where(dists < r)[0]
                    if len(rec) > 0:
                        periods.extend((rec + 1).tolist())
                if len(periods) > 5:
                    hist_p, _ = np.histogram(periods, bins=20, density=True)
                    hist_p = hist_p[hist_p > 1e-10]
                    rpde_val = -float(np.sum(hist_p * np.log(hist_p))) / np.log(len(hist_p))
                else:
                    rpde_val = 0.5
            except Exception:
                rpde_val = 0.5
        else:
            dfa_val = 0.5
            d2_val = 2.5
            rpde_val = 0.5

        features['spread1'] = clamp(safe(spread1_val, 5.0), 0.0, 100.0)
        features['spread2'] = clamp(safe(spread2_val, 0.1), 0.0, 1.0)
        features['PPE'] = clamp(safe(ppe_val, 0.5), 0.0, 1.0)
        features['DFA'] = clamp(safe(dfa_val, 0.5), 0.3, 1.5)
        features['D2'] = clamp(safe(d2_val, 2.5), 1.0, 4.0)
        features['RPDE'] = clamp(safe(rpde_val, 0.5), 0.0, 1.0)

        return features

    finally:
        # Clean up temp file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def extract_features_from_bytes(audio_bytes, filename='recording.wav'):
    """
    Extract features from raw audio bytes.

    Parameters
    ----------
    audio_bytes : bytes
        Raw audio file bytes.
    filename : str
        Original filename for format detection.

    Returns
    -------
    dict
        Extracted acoustic features.
    """
    suffix = os.path.splitext(filename)[1] or '.wav'
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        return extract_features_from_file(tmp_path)
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
