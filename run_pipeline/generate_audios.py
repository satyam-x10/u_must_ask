import os
import json
import time
from scripts.vits import generate_tts_audio
# from scripts.bark import generate_tts_audio

def generate_audios(filepath: str) -> list:
    
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    # Read JSON
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "scenes" not in data:
        raise ValueError("Invalid JSON format — missing 'scenes' key.")

    title = data.get("title", "Untitled Project")
    scenes = data["scenes"]

    # Extract script ID from filename (script_1.json → 1)
    filename = os.path.basename(filepath)             # script_1.json
    script_id = filename.replace("script_", "").replace(".json", "")  # 1

    # NEW destination folder
    audio_dir = os.path.join("outputs", "audios", script_id)
    os.makedirs(audio_dir, exist_ok=True)

    print(f"\nGenerating audios for project: {title} ({len(scenes)} scenes)\n")

    generated = []

    for scene in scenes:
        scene_id = scene.get("id", "unknown")
        text = scene.get("text", "").strip()
        emotion = scene.get("emotion", "excited")

        if not text:
            print(f"Scene {scene_id} has no text, skipping.")
            continue

        filename = f"scene_{scene_id}.wav"
        output_path = os.path.join(audio_dir, filename)

        try:
            path = generate_tts_audio(text, output_path, emotion)
            generated.append(path)
        except Exception as e:
            print(f"Error generating scene {scene_id}: {e}")

        time.sleep(0.2)

    print(f"\nFinished. {len(generated)} audio files saved in {audio_dir}")
    return generated
