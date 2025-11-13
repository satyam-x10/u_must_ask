import os
import time
from TTS.api import TTS
from pydub import AudioSegment

# ---------- CONFIG ----------
MODEL_NAME = "tts_models/en/vctk/vits"  # Multi-speaker model
DEFAULT_SPEAKER = "p227"
# ----------------------------

# Load the model once globally
print(f"🎙️ Loading model: {MODEL_NAME}")
tts = TTS(model_name=MODEL_NAME, progress_bar=False, gpu=False)

def generate_tts_audio(text: str, output_path: str) -> str:
   
    if not text or not text.strip():
        raise ValueError("Text cannot be empty.")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    try:
        tts.tts_to_file(text=text, speaker=DEFAULT_SPEAKER, file_path=output_path)
        AudioSegment.from_wav(output_path)  # Validate
    except Exception as e:
        print(f"⚠️ Error generating audio: {e}")
        raise e

    time.sleep(0.1)  # Prevent file lock issues on Windows
    print(f"✅ Audio saved: {output_path}")
    return output_path
