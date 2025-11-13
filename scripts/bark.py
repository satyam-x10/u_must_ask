import os
import time
from bark import SAMPLE_RATE, generate_audio, preload_models
from scipy.io.wavfile import write as write_wav

# --------- SETUP ---------
print("Loading Bark models...")
preload_models()

# Default Bark speaker (choose any from the list below)
DEFAULT_SPEAKER = "v2/en_speaker_6"

# Emotion → text prompt injection
EMOTION_TAGS = {
    "happy":     "[laughs softly, cheerful tone]",
    "excited":   "[high energy, enthusiastic tone!]",
    "surprised": "[gasp, astonished tone!]",
    "calm":      "[soft, calm tone]",
    "sad":       "[slow, sad tone, sighs]",
    "angry":     "[sharp tone, frustrated]",
}

# -------------------------


def generate_tts_audio(text: str, output_path: str, emotion: str = "calm") -> str:
    if not text or not text.strip():
        raise ValueError("Text cannot be empty.")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Build emotional prompt
    emotion_prefix = EMOTION_TAGS.get(emotion, EMOTION_TAGS["calm"])
    final_text = f"{emotion_prefix} {text}"

    try:
        audio_array = generate_audio(
            final_text,
            history_prompt=DEFAULT_SPEAKER
        )

        write_wav(output_path, SAMPLE_RATE, audio_array)

    except Exception as e:
        print(f"Error generating Bark audio ({emotion}): {e}")
        raise e

    time.sleep(0.1)
    print(f"Audio saved ({emotion}): {output_path}")
    return output_path
