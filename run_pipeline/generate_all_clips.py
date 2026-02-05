import os
import json
import wave
import contextlib
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
        # Default guess (Legacy)
        image_path = os.path.join(images_dir, f"scene_{scene_id}.png")
        
        # Check for NEW nested structure: scene_{id}/img_1.png
        scene_subfolder = os.path.join(images_dir, f"scene_{scene_id}")
        if os.path.exists(scene_subfolder):
            # Prefer img_1.png as the "main" one for the batch list
            # The interactive batch processor will find the rest
            potential_main = os.path.join(scene_subfolder, "img_1.png")
            if os.path.exists(potential_main):
                image_path = potential_main
        
        # Fallback: Check for flat indexed variants scene_{id}_1.png
        elif not os.path.exists(image_path):
            for i in range(1, 4):
                 alt = os.path.join(images_dir, f"scene_{scene_id}_{i}.png")
                 if os.path.exists(alt):
                     image_path = alt
                     break
        
        audio_path = os.path.join(audios_dir, f"scene_{scene_id}.wav")
        output_path = os.path.join(clips_dir, f"scene_{scene_id}.mp4")

        # Basic existence check (image_path must exist by now or we skip)
        if not os.path.exists(image_path):
             # Try one more time to just check if folder exists, maybe img_1 is missing but img_2 exists?
             # For simplicity, we assume img_1 is the anchor.
             # Actually, let's be robust:
             if os.path.exists(scene_subfolder):
                 for i in range(1, 4):
                     alt = os.path.join(scene_subfolder, f"img_{i}.png")
                     if os.path.exists(alt):
                         image_path = alt
                         break

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
        # Same checks
        if not os.path.exists(image_path):
             for i in range(1, 4):
                 alt = os.path.join(images_dir, f"scene_{scene_id}_{i}.png")
                 if os.path.exists(alt):
                     image_path = alt
                     break
                     
        if not os.path.exists(image_path) or not os.path.exists(audio_path): continue
        if os.path.exists(output_path): continue # If batch made it, we skip

        print(f"Generating STATIC clip for scene {scene_id} (Fallback)...")
        generate_scene_clip(image_path, audio_path, output_path, audio_text)

    print("All clips generated successfully.")

    # ---------------------------------------------------------
    # Generate audio.json (Cumulative Metadata)
    # ---------------------------------------------------------
    print(f"\n[Metadata] Generating audio.json for folder {script_id}...")
    
    audio_meta = {
        "script_id": script_id,
        "segments": []
    }
    
    total_duration = 0.0
    
    for scene in script["scenes"]:
        scene_id = scene["id"]
        audio_path = os.path.join(audios_dir, f"scene_{scene_id}.wav")
        
        if not os.path.exists(audio_path):
            continue
            
        # Get Duration using wave (faster/lighter than MoviePy for just duration)
        duration = 0.0
        try:
            with contextlib.closing(wave.open(audio_path, 'r')) as f:
                frames = f.getnframes()
                rate = f.getframerate()
                duration = frames / float(rate)
        except Exception as e:
            print(f"Warning: Could not read duration for {audio_path}: {e}")
            
        start_time = total_duration
        end_time = total_duration + duration
        
        audio_meta["segments"].append({
            "scene_id": scene_id,
            "file": f"scene_{scene_id}.wav",
            "text": scene.get("text", ""),
            "duration": duration,
            "start_time": round(start_time, 3),
            "end_time": round(end_time, 3)
        })
        
        total_duration = end_time

    audio_meta["total_duration_result"] = round(total_duration, 3)
    
    # Save to audio folder
    json_out_path = os.path.join(audios_dir, "audio.json")
    with open(json_out_path, "w", encoding="utf-8") as f:
        json.dump(audio_meta, f, indent=4)
        
    print(f"[Metadata] Saved audio.json to {json_out_path}")
