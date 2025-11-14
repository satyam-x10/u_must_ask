import os
import time
from TTS.api import TTS
from pydub import AudioSegment

# ---------- CONFIG ----------
MODEL_NAME = "tts_models/en/vctk/vits"  # Multi-speaker
DEFAULT_SPEAKER = "p236"

# 236,237

# | ID       | Notes                                      |
# | -------- | ------------------------------------------ |
# | **p225** | Clear bright female voice                  |
# | **p227** | Neutral, soft female voice (great default) |
# | **p229** | Warm tone, smooth female voice             |
# | **p231** | Slightly energetic, expressive             |
# | **p233** | Calm, lower pitch female                   |
# | **p236** | Youthful, friendly tone                    |
# | **p239** | Balanced, clean female voice               |
# | **p240** | Slightly deeper female voice               |


# | ID       | Notes                                |
# | -------- | ------------------------------------ |
# | **p226** | Neutral, clean male voice            |
# | **p228** | Young energetic male                 |
# | **p230** | Deep rich male voice                 |
# | **p232** | Calm and smooth                      |
# | **p234** | Slightly sharper tone                |
# | **p237** | Strong expressive male tone          |
# | **p238** | Warm and natural-sounding male voice |


# Emotion → prosody presets
EMOTION_PRESETS = {
    "happy":     {"speed": 1.10, "temperature": 0.9,  "glow_tts_alpha": 0.6},
    "excited":   {"speed": 1.18, "temperature": 1.0,  "glow_tts_alpha": 0.5},
    "surprised": {"speed": 1.22, "temperature": 1.1,  "glow_tts_alpha": 0.6},
    "calm":      {"speed": 0.92, "temperature": 0.6,  "glow_tts_alpha": 1.1},
    "sad":       {"speed": 0.88, "temperature": 0.55, "glow_tts_alpha": 1.2},
    "angry":     {"speed": 1.05, "temperature": 1.2,  "glow_tts_alpha": 0.4},
}

# ----------------------------

print(f"🎙️ Loading model: {MODEL_NAME}")
tts = TTS(model_name=MODEL_NAME, progress_bar=False, gpu=False)


def generate_tts_audio(text: str, output_path: str, emotion: str = "calm") -> str:
    
    if not text or not text.strip():
        raise ValueError("Text cannot be empty.")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Choose emotion preset or fallback to calm
    preset = EMOTION_PRESETS.get(emotion, EMOTION_PRESETS["calm"])

    try:
        tts.tts_to_file(
        text=text,
        file_path=output_path,
        speed=preset["speed"],
        temperature=preset["temperature"],
        glow_tts_alpha=preset["glow_tts_alpha"],
        speaker=DEFAULT_SPEAKER
        )


        AudioSegment.from_wav(output_path)  # Validate WAV

    except Exception as e:
        print(f"⚠️ Error generating audio ({emotion}): {e}")
        raise e

    time.sleep(0.1)  # Avoid Windows file locks
    print(f"✅ Audio saved ({emotion}): {output_path}")
    return output_path
