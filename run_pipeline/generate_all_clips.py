import os
import json
from scripts.clip import generate_scene_clip

def generate_all_clips(filepath_to_script: str):
    base_dir = os.path.dirname(filepath_to_script)
    """Iterate through scenes in script.json and generate videos for each."""
    script_path = os.path.join(base_dir, "script.json")
    audios_dir = os.path.join(base_dir, "audios")
    images_dir = os.path.join(base_dir, "images")
    clips_dir = os.path.join(base_dir, "clips")

    # Create clips directory if not exists
    os.makedirs(clips_dir, exist_ok=True)

    # Load script.json
    with open(script_path, "r", encoding="utf-8") as f:
        script = json.load(f)

    # Iterate through all scenes
    for scene in script["scenes"]:
        scene_id = scene["id"]
        image_path = os.path.join(images_dir, f"scene_{scene_id}.png")
        audio_path = os.path.join(audios_dir, f"scene_{scene_id}.wav")
        output_path = os.path.join(clips_dir, f"scene_{scene_id}.mp4")

        if not os.path.exists(image_path) or not os.path.exists(audio_path):
            print(f"Skipping scene {scene_id}: Missing image or audio.")
            continue

        print(f"Generating video for scene {scene_id}...")
        generate_scene_clip(image_path, audio_path, output_path)

    print("✅ All clips generated successfully!")

