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

# Generate Full Audio (Concatenated)
print("\n🔗 Generating full audio file (concatenated)...")
full_audio = AudioSegment.empty()

# Iterate again to ensure correct order or just load them
# Since we processed sequentially, we can just load them by filename
for idx in range(1, len(scenes) + 1):
    file_path = os.path.join(OUTPUT_DIR, f"scene_{idx:03d}.wav")
    if os.path.exists(file_path):
        segment = AudioSegment.from_wav(file_path)
        full_audio += segment
        
        # Get delay from script scene data corresponding to this index
        # index is 1-based, scenes listing is 0-based
        if idx <= len(scenes):
             current_scene = scenes[idx-1]
             delay_sec = current_scene.get("audio_delay", 0.5)
             delay_ms = int(delay_sec * 1000)
             full_audio += AudioSegment.silent(duration=delay_ms)
             
    else:
        print(f"⚠️ Warning: Missing audio for scene {idx}")

full_audio_path = os.path.join(OUTPUT_DIR, "full_audio.wav")
full_audio.export(full_audio_path, format="wav")
print(f"✅ Full audio saved: {full_audio_path}")

print(f"\n🎧 All audio clips saved in: {OUTPUT_DIR}")
