import librosa
import numpy as np
import os

def analyze_audio_confidence(audio_path):
    """
    Reads audio and computes simple features:
    - avg_pitch (approx)
    - avg_energy
    - filler_word_count (placeholder: 0)
    - hesitation_count (based on long silences)
    Returns a dict.
    """
    try:
        y, sr = librosa.load(audio_path, sr=16000)
    except Exception as e:
        return {"error": "audio read failed: " + str(e)}

    # energy
    energy = np.mean(librosa.feature.rms(y=y))
    # approximate pitch via zero-crossing rate as placeholder
    zcr = np.mean(librosa.feature.zero_crossing_rate(y))
    # detect long silences -> hesitation
    intervals = librosa.effects.split(y, top_db=35)
    # count gaps
    total_duration = len(y) / sr
    speech_duration = sum((end - start) for start,end in intervals) / sr
    silence_duration = total_duration - speech_duration
    hesitation_count = int(silence_duration // 1)  # 1-second silence approximated

    return {
        "avg_energy": float(energy),
        "avg_zcr": float(zcr),
        "hesitation_count": hesitation_count,
        "speech_duration": speech_duration,
        "total_duration": total_duration,
        "filler_word_count": 0  # advanced: use ASR + detect "um/uh"
    }
