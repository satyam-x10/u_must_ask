import os
import json
from scripts.clip import generate_scene_clip

def generate_all_clips(filepath_to_script: str):
    

    # Extract script ID from filename
    filename = os.path.basename(filepath_to_script)          # script_12.json
    script_id = filename.replace("script_", "").replace(".json", "")  # 12

    # Base folder
    BASE = "outputs"

    # Directories
    script_path = filepath_to_script
    images_dir = os.path.join(BASE, "images", script_id)
    audios_dir = os.path.join(BASE, "audios", script_id)
    clips_dir  = os.path.join(BASE, "clips", script_id)

    # Create output folder
    os.makedirs(clips_dir, exist_ok=True)

    # Load script
    with open(script_path, "r", encoding="utf-8") as f:
        script = json.load(f)

    # Iterate scenes
    for scene in script["scenes"]:
        scene_id = scene["id"]

        audio_text = scene.get("text", "").strip()

        image_path = os.path.join(images_dir, f"scene_{scene_id}.png")
        audio_path = os.path.join(audios_dir, f"scene_{scene_id}.wav")
        output_path = os.path.join(clips_dir, f"scene_{scene_id}.mp4")
        

        if not os.path.exists(image_path):
            print(f"Skipping scene {scene_id}: missing image — {image_path}")
            continue

        if not os.path.exists(audio_path):
            print(f"Skipping scene {scene_id}: missing audio — {audio_path}")
            continue

        print(f"Generating clip for scene {scene_id}...")
        generate_scene_clip(image_path, audio_path, output_path,audio_text)

    print("All clips generated successfully.")
