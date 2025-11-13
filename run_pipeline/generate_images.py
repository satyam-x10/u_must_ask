import os
import json
import time
from scripts.kandisky import generate_image_from_prompt

def generate_images(filepath: str) -> list:

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    # Read raw content first
    with open(filepath, "r", encoding="utf-8") as f:
        raw_content = f.read()

    # Try parsing JSON
    try:
        data = json.loads(raw_content)
        is_valid_json = True
    except Exception:
        is_valid_json = False

    # If not valid JSON, save raw content to a .txt file and exit
    if not is_valid_json:
        txt_path = filepath + ".txt"

        with open(txt_path, "w", encoding="utf-8") as txt:
            txt.write(raw_content)

        print("\n❌ Invalid JSON detected.")
        print(f"📄 Raw content saved as text file: {txt_path}\n")

        return [txt_path]

    # Continue if JSON is valid
    if "scenes" not in data:
        raise ValueError("Invalid JSON format — missing 'scenes' key.")

    title = data.get("title", "Untitled Project")
    scenes = data["scenes"]

    # Create output folder
    base_dir = os.path.dirname(filepath)
    image_dir = os.path.join(base_dir, "images")
    os.makedirs(image_dir, exist_ok=True)

    print(f"\n🖼️ Generating images for project: {title} ({len(scenes)} scenes)\n")

    generated = []

    for scene in scenes[0:3]:
        scene_id = scene.get("id", "unknown")
        prompt = scene.get("prompt", "").strip()
        text = scene.get("text", "").strip()

        if not prompt:
            print(f"⚠️ Scene {scene_id} has no prompt, skipping.")
            continue

        filename = f"scene_{scene_id}.png"
        output_path = os.path.join(image_dir, filename)

        try:
            path = generate_image_from_prompt(prompt, output_path, text)
            generated.append(path)
        except Exception as e:
            print(f"⚠️ Error generating scene {scene_id}: {e}")

        time.sleep(0.2)

    print(f"\n✅ Finished. {len(generated)} images saved in {image_dir}")
    return generated
