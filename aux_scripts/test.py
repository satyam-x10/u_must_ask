import os
import time
from bark import SAMPLE_RATE, generate_audio, preload_models
from scipy.io.wavfile import write as write_wav

# --------- SETUP ---------
print("Loading Bark models...")
preload_models()

DEFAULT_SPEAKER = "v2/en_speaker_6"

# Emotion → prompt tags
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

    # Apply emotion tag
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


# --------------------------------------------------
# NEW: Generate multiple lines with different tones
# --------------------------------------------------

def generate_multiple_tts(entries, output_folder="outputs/audio"):
    os.makedirs(output_folder, exist_ok=True)

    for i, item in enumerate(entries, start=1):
        text = item["text"]
        emotion = item.get("emotion", "calm")

        # Clean friendly filename
        filename = f"audio_{i:03d}_{emotion}.wav"
        output_path = os.path.join(output_folder, filename)

        print(f"\n▶ Generating line {i}: {emotion.upper()} → {text}")
        generate_tts_audio(text, output_path, emotion)

    print("\nAll audios generated.")


# --------------------------------------------------
# EXAMPLE USAGE
# --------------------------------------------------
if __name__ == "__main__":
    lines = [
        {"text": "Hello, how are you today?", "emotion": "calm"},
        {"text": "Wow! That's amazing!", "emotion": "excited"},
        {"text": "I can't believe this happened...", "emotion": "sad"},
        {"text": "What are you doing here?", "emotion": "angry"},
        {"text": "Oh! I didn’t expect that!", "emotion": "surprised"},
    ]

    generate_multiple_tts(lines)
