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

    # If invalid JSON, save raw text
    if not is_valid_json:
        txt_path = filepath + ".txt"

        with open(txt_path, "w", encoding="utf-8") as txt:
            txt.write(raw_content)

        print("\nInvalid JSON detected.")
        print(f"Raw content saved as text file: {txt_path}\n")

        return [txt_path]

    # Continue if JSON is valid
    if "scenes" not in data:
        raise ValueError("Invalid JSON format — missing 'scenes' key.")

    title = data.get("title", "Untitled Project")
    scenes = data["scenes"]

    # Extract script ID from filename
    filename = os.path.basename(filepath)                 # script_1.json
    script_id = filename.replace("script_", "").replace(".json", "")

    # NEW OUTPUT DIRECTORY
    image_dir = os.path.join("outputs", "images", script_id)
    os.makedirs(image_dir, exist_ok=True)

    print(f"\nGenerating images for project: {title} ({len(scenes)} scenes)\n")

    generated = []

    for scene in scenes:
        scene_id = scene.get("id", "unknown")
        
        # Support both 'image_prompts' (list) and legacy 'image_prompt' (str)
        prompts = scene.get("image_prompts", [])
        if not prompts:
             single_prompt = scene.get("image_prompt", "")
             if single_prompt:
                 prompts = [single_prompt]
        
        if not prompts:
            print(f"Scene {scene_id} has no prompts, skipping.")
            continue

        # Create scene_id folder
        scene_dir = os.path.join(image_dir, f"scene_{scene_id}")
        os.makedirs(scene_dir, exist_ok=True)

        for i, prompt in enumerate(prompts, start=1):
            if not prompt.strip():
                continue
                
            # filename: img_1.png, img_2.png inside scene_X folder
            filename = f"img_{i}.png" 
            output_path = os.path.join(scene_dir, filename)

            if os.path.exists(output_path):
                 print(f"  -> {filename} already exists in scene_{scene_id}, skipping.")
                 generated.append(output_path)
                 continue

            try:
                print(f"Generating scene {scene_id} image {i}...")
                path = generate_image_from_prompt(prompt, output_path)
                generated.append(path)
            except Exception as e:
                print(f"Error generating scene {scene_id} image {i}: {e}")
            
            time.sleep(0.2)

    print(f"\nFinished. {len(generated)} images saved in {image_dir}")
    return generated
