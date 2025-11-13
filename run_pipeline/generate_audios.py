import os
import json
import time
from scripts.vits import generate_tts_audio

def generate_audios(filepath: str) -> list:
    # Example: "outputs/1/script.json"
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "scenes" not in data:
        raise ValueError("Invalid JSON format — missing 'scenes' key.")

    title = data.get("title", "Untitled Project")
    scenes = data["scenes"]

    # Determine audio output folder based on JSON file path
    base_dir = os.path.dirname(filepath)
    audio_dir = os.path.join(base_dir, "audios")
    os.makedirs(audio_dir, exist_ok=True)

    print(f"\n🎧 Generating audios for project: {title} ({len(scenes)} scenes)\n")

    generated = []

    for scene in scenes:
        scene_id = scene.get("id", "unknown")
        text = scene.get("text", "").strip()

        if not text:
            print(f"⚠️ Scene {scene_id} has no text, skipping.")
            continue

        filename = f"scene_{scene_id}.wav"
        output_path = os.path.join(audio_dir, filename)

        try:
            path = generate_tts_audio(text, output_path)
            generated.append(path)
        except Exception as e:
            print(f"⚠️ Error generating scene {scene_id}: {e}")

        time.sleep(0.2)

    print(f"\n✅ Finished. {len(generated)} audio files saved in {audio_dir}")
