import os
import time
from TTS.api import TTS
from pydub import AudioSegment

MODEL_NAME = "tts_models/multilingual/multi-dataset/xtts_v2"
DEFAULT_EMOTION = "excited"    # Options: neutral, happy, sad, angry, excited, whisper, shouting
DEFAULT_SPEED = 1.05           # Slightly faster feels more energetic

print(f"🎙️ Loading expressive model: {MODEL_NAME}")
tts = TTS(model_name=MODEL_NAME, progress_bar=False, gpu=False)

def generate_tts_audio(text: str, output_path: str, emotion=DEFAULT_EMOTION) -> str:
    
    if not text.strip():
        raise ValueError("Text cannot be empty.")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    try:
        tts.tts_to_file(
            text=text,
            file_path=output_path,
            emotion=emotion,
            speed=DEFAULT_SPEED,
            temperature=0.8,  # More variation in tone
        )
        AudioSegment.from_wav(output_path)  # validate file
    except Exception as e:
        print(f"⚠️ Error generating audio: {e}")
        raise e

    time.sleep(0.1)
    print(f"✅ Expressive audio saved: {output_path}")
    return output_path
