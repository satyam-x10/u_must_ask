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
    
    use_interactive = input("\nEnable Interactive Mode? (This will require manual verification for each clip) [y/N]: ").strip().lower() == 'y'
    
    # Collect scenes for batch processing
    batch_scenes = []
    
    # First pass: Identify what needs to be made
    for scene in script["scenes"]:
        scene_id = scene["id"]
        image_path = os.path.join(images_dir, f"scene_{scene_id}.png")
        audio_path = os.path.join(audios_dir, f"scene_{scene_id}.wav")
        output_path = os.path.join(clips_dir, f"scene_{scene_id}.mp4")

        if not os.path.exists(image_path) or not os.path.exists(audio_path):
            continue
            
        if os.path.exists(output_path):
            print(f"Skipping scene {scene_id}: clip already exists")
            continue
            
        scene_data = {
            "id": scene_id,
            "image_path": image_path,
            "audio_path": audio_path,
            "output_path": output_path,
            "audio_text": scene.get("text", "")
        }
        batch_scenes.append(scene_data)

    # Run Batch Processor if interactive
    from scripts.interactive_clip import run_batch_processor
    
    if use_interactive and batch_scenes:
        print(f"\n[Main] Sending {len(batch_scenes)} scenes to Batch Processor...")
        run_batch_processor(batch_scenes)
        
    # Final Pass: Check exists (Batch might have skipped some) and generate static fallback
    for scene in script["scenes"]:
        scene_id = scene["id"]
        image_path = os.path.join(images_dir, f"scene_{scene_id}.png")
        audio_path = os.path.join(audios_dir, f"scene_{scene_id}.wav")
        output_path = os.path.join(clips_dir, f"scene_{scene_id}.mp4")
        audio_text = scene.get("text", "") # Getting text again

        # Same checks
        if not os.path.exists(image_path) or not os.path.exists(audio_path): continue
        if os.path.exists(output_path): continue # If batch made it, we skip

        print(f"Generating STATIC clip for scene {scene_id} (Fallback)...")
        generate_scene_clip(image_path, audio_path, output_path, audio_text)

    print("All clips generated successfully.")
