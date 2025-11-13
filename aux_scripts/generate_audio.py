import os
import json
import time
from pydub import AudioSegment
from TTS.api import TTS

# ---------- CONFIG ----------
CONFIG_FILE = "config.json"
SCRIPT_FILE = "script.json"
OUTPUT_DIR = "outputs/audio"
PAUSE_DURATION_MS = 300
USE_GPU = False
MODEL_NAME = "tts_models/en/vctk/vits"
# ----------------------------

# === Load Config ===
with open(CONFIG_FILE, "r", encoding="utf-8") as f:
    config = json.load(f)

VOICE = config.get("voice", "p229")

os.makedirs(OUTPUT_DIR, exist_ok=True)

print(f"🎙 Loading TTS model: {MODEL_NAME} | Voice: {VOICE}")
tts = TTS(model_name=MODEL_NAME, progress_bar=True, gpu=USE_GPU)

# === Load Script ===
with open(SCRIPT_FILE, "r", encoding="utf-8") as f:
    script_data = json.load(f)

scenes = script_data["scenes"]
print(f"\n🎬 Generating {len(scenes)} audio lines...\n")

for idx, scene in enumerate(scenes, start=1):
    text = scene["text"].strip()
    line_filename = f"scene_{idx:03d}.wav"
    line_path = os.path.join(OUTPUT_DIR, line_filename)

    print(f"[{idx}] {VOICE}: {text}")

    try:
        tts.tts_to_file(
            text=text,
            speaker=VOICE,
            file_path=line_path
        )

        # Add short pause padding
        if PAUSE_DURATION_MS > 0:
            audio = AudioSegment.from_wav(line_path)
            padded = audio + AudioSegment.silent(duration=PAUSE_DURATION_MS)
            padded.export(line_path, format="wav")

        print(f"✅ Saved: {line_path}")

    except Exception as e:
        print(f"❌ Error on scene {idx}: {e}")

    time.sleep(0.1)

print(f"\n🎧 All audio clips saved in: {OUTPUT_DIR}")
