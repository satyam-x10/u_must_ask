import os
import time
import re
from TTS.api import TTS
from pydub import AudioSegment

# ==============================================================
# CONFIG
# ==============================================================

MODEL_NAME = "tts_models/en/vctk/vits"  # Multi-speaker VITS

EMOTION_PRESETS = {
    "happy":     {"speed": 1.10, "temperature": 0.9,  "glow_tts_alpha": 0.6},
    "excited":   {"speed": 1.18, "temperature": 1.0,  "glow_tts_alpha": 0.5},
    "surprised": {"speed": 1.22, "temperature": 1.1,  "glow_tts_alpha": 0.6},
    "calm":      {"speed": 0.92, "temperature": 0.6,  "glow_tts_alpha": 1.1},
    "sad":       {"speed": 0.88, "temperature": 0.55, "glow_tts_alpha": 1.2},
    "angry":     {"speed": 1.05, "temperature": 1.2,  "glow_tts_alpha": 0.4},
}

print(f"🎙️ Loading model: {MODEL_NAME}")
tts = TTS(model_name=MODEL_NAME, progress_bar=False, gpu=False)

# ==============================================================
# FILE NAME SANITIZER
# ==============================================================

def sanitize(name: str) -> str:
    return re.sub(r'[\\/*?:"<>|\n\r\t ]+', "_", name).strip("_")

# ==============================================================
# FIXED FUNCTION — NOW ACCEPTS SPEAKER
# ==============================================================

def generate_tts_audio(text: str, output_path: str, speaker: str, emotion: str = "calm") -> str:

    if not text or not text.strip():
        raise ValueError("Text cannot be empty.")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    preset = EMOTION_PRESETS.get(emotion, EMOTION_PRESETS["calm"])

    try:
        tts.tts_to_file(
            text=text,
            file_path=output_path,
            speaker=speaker,  # REQUIRED
            speed=preset["speed"],
            temperature=preset["temperature"],
            glow_tts_alpha=preset["glow_tts_alpha"],
        )

        AudioSegment.from_wav(output_path)

    except Exception as e:
        print(f"⚠️ Error generating audio ({speaker} - {emotion}): {e}")
        raise e

    time.sleep(0.1)
    print(f"✅ Audio saved ({speaker}): {output_path}")
    return output_path

# ==============================================================
# SPEAKER TEST LINES
# ==============================================================

TEST_LINES = [
    "Hello, this is a quick voice test.",
    "You are now listening to the VITS speaker sample."
]

# ==============================================================
# LOOP THROUGH ALL SPEAKERS
# ==============================================================

def test_all_vits_speakers():
    output_dir = "outputs/vits_speakers"
    os.makedirs(output_dir, exist_ok=True)

    speakers = tts.speakers
    print(f"\nFound {len(speakers)} speakers.")

    for spk in speakers:
        safe_name = sanitize(spk)
        print(f"\n🔊 Testing speaker: {spk}  →  {safe_name}")

        for idx, line in enumerate(TEST_LINES, start=1):
            output_path = os.path.join(output_dir, f"{safe_name}_line{idx}.wav")

            try:
                generate_tts_audio(
                    text=line,
                    output_path=output_path,
                    speaker=spk,       # FIXED
                    emotion="calm"
                )
            except Exception as e:
                print(f"⚠️ Error for speaker {spk}: {e}")

    print("\n✅ All VITS speaker samples generated.")

# ==============================================================
# RUN SCRIPT
# ==============================================================

if __name__ == "__main__":
    test_all_vits_speakers()
