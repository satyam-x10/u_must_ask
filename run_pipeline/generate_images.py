import os
import json
import time
from scripts.kandisky import generate_image_from_prompt

def generate_images(filepath: str) -> list:
    
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "scenes" not in data:
        raise ValueError("Invalid JSON format — missing 'scenes' key.")

    title = data.get("title", "Untitled Project")
    scenes = data["scenes"]

    # Determine image output folder based on JSON file path
    base_dir = os.path.dirname(filepath)
    image_dir = os.path.join(base_dir, "images")
    os.makedirs(image_dir, exist_ok=True)

    print(f"\n🖼️ Generating images for project: {title} ({len(scenes)} scenes)\n")

    generated = []

    for scene in scenes:
    # for scene in scenes:
        scene_id = scene.get("id", "unknown")
        prompt = scene.get("prompt", "").strip()
        text = scene.get("text", "").strip()

        if not prompt:
            print(f"⚠️ Scene {scene_id} has no prompt, skipping.")
            continue

        filename = f"scene_{scene_id}.png"
        output_path = os.path.join(image_dir, filename)

        try:
            path = generate_image_from_prompt(prompt, output_path,text)
            generated.append(path)
        except Exception as e:
            print(f"⚠️ Error generating scene {scene_id}: {e}")

        time.sleep(0.2)

    print(f"\n✅ Finished. {len(generated)} images saved in {image_dir}")
    return image_dir
