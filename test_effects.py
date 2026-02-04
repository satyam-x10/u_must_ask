
import os
import sys

# Ensure we can import from local scripts
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.interactive_clip import extract_layers, generate_single_clip_from_data

def test_all_effects():
    print("========================================")
    print("      Testing All 10 Effects            ")
    print("========================================")

    # 1. Setup Paths (Assumption: Script ID 1 exists)
    script_id = "1" 
    base_dir = "outputs"
    
    img_path = os.path.join(base_dir, "images", script_id, "scene_1.png")
    audio_path = os.path.join(base_dir, "audios", script_id, "scene_1.wav")
    
    output_dir = os.path.join("test_outputs")
    os.makedirs(output_dir, exist_ok=True)
    
    if not os.path.exists(img_path) or not os.path.exists(audio_path):
        print(f"Error: Could not find Scene 1 assets at {img_path}")
        print("Please ensure you have generated assets for Script 1.")
        # Fallback check for Scene 6 just in case
        img_path = os.path.join(base_dir, "images", script_id, "scene_6.png")
        audio_path = os.path.join(base_dir, "audios", script_id, "scene_6.wav")
        if not os.path.exists(img_path):
             return

    # 2. Extract Layers (Once)
    print(f"\n[1/3] Extracting Layers for {img_path}...")
    fg, bg, orig = extract_layers(img_path)
    print("Extraction Complete.")

    # 3. Define Effects Map with Descriptions (Pruned List)
    effects = [
        ("1", "Zoom Subject", "Strong zoom on subject (1.15x) + subtle BG zoom"),
        ("2", "Parallax", "Subject moves Right, BG moves Left (3D slide)"),
        ("3", "Floating", "Subject bobs up and down (Ghost/Hover)"),
        ("4", "Zoom BG", "Background zooms in, subject stays centered"),
        ("5", "Shake (Glitch)", "Random jitter/vibration (Update 6fps)"),
        ("6", "BW to Color", "Fades from Grayscale to Full Color"),
        ("7", "Flash Strobe", "Energetic brightness pulses/flashing"),
        ("8", "Vignette Pulse", "Dark pulsing corners/edges"),
        ("9", "Spotlight", "Darkened Background, bright Subject")
    ]

    # 4. Generate Loop
    print(f"\n[2/3] Generating {len(effects)} Clips...")
    
    for choice, name, desc in effects:
        print(f"\n---> Generating Effect {choice}: {name}")
        print(f"     Description: {desc}")
        
        filename = f"effect_{choice}_{name.replace(' ', '_').lower()}.mp4"
        out_path = os.path.join(output_dir, filename)
        
        # Audio Text for Caption Testing
        sample_text = f"Effect {choice}: {name}"
        
        try:
            success = generate_single_clip_from_data(
                fg, bg, choice, audio_path, out_path, audio_text=sample_text
            )
            if success:
                print(f"     [SUCCESS] Saved to {out_path}")
            else:
                print(f"     [FAILED] returned False")
                
        except Exception as e:
            print(f"     [ERROR] {e}")

    print("\n========================================")
    print(f"Done! Check the '{output_dir}' folder.")
    print("========================================")

if __name__ == "__main__":
    test_all_effects()
