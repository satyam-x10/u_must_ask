import re
import json
import os
from json_repair import repair_json
from llm.generate_script import generate_script
from scripts.prompt import build_educational_script_prompt, build_scene_generation_prompt

OUTPUT_DIR = "outputs"
MAX_RETRIES = 5


def extract_first_json_block(text: str) -> str:
    """
    Extract the first { ... } block by bracket counting.
    Works even if text contains garbage before/after JSON.
    """
    start = text.find("{")
    if start == -1:
        return None

    depth = 0
    for i, ch in enumerate(text[start:], start=start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
    return None

def generate_Script_Gemini(TITLE_NAME, TITLE_ID):

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # ---------------------------------------------------------
    # STEP 1: Generate Educational Script (Text Only)
    # ---------------------------------------------------------
    print(f"\n[Step 1] Generating Educational Script for: {TITLE_NAME}...")
    prompt_text = build_educational_script_prompt(TITLE_NAME)
    educational_script_text = generate_script(prompt_text)
    
    if not educational_script_text or len(educational_script_text) < 100:
         print("Error: Generated script text is too short.")
         return None

    print(f"[Step 1] Script generated ({len(educational_script_text)} chars). Proceeding to Scene generation...")

    # ---------------------------------------------------------
    # STEP 2: Convert to JSON Scenes (with Retry)
    # ---------------------------------------------------------
    prompt_json = build_scene_generation_prompt(educational_script_text)
    
    script_data = None
    raw_output = ""

    for attempt in range(1, MAX_RETRIES + 1):

        print(f"\n[Step 2] Attempt {attempt}/{MAX_RETRIES} for JSON Conversion...")

        raw_output = generate_script(prompt_json)

        cleaned = re.sub(r"```(?:json)?|```", "", raw_output).strip()

        block = extract_first_json_block(cleaned)
        if not block:
            print("No JSON block. Retrying...")
            continue

        try:
            script_data = json.loads(block)
        except:
            try:
                repaired = repair_json(block)
                script_data = json.loads(repaired)
                print("JSON repaired successfully.")
            except:
                print("JSON unrecoverable. Retrying...")
                continue

        if "scenes" not in script_data:
            print("'scenes' missing. Retrying...")
            continue

        if not isinstance(script_data["scenes"], list) or len(script_data["scenes"]) < 5:
            print("Invalid scenes array (too short). Retrying...")
            continue
            
        # Validate Image Prompts
        valid_images = True
        for scene in script_data["scenes"]:
            if "image_prompts" not in scene or not isinstance(scene["image_prompts"], list) or len(scene["image_prompts"]) != 3:
                 print(f"Invalid image_prompts in scene {scene.get('id')}. Must be list of 3.")
                 valid_images = False
                 break
        
        if not valid_images:
            continue

        print("Valid script generated.")
        break

    if script_data is None:
        script_data = {
            "error": "Failed to generate valid script after retries.",
            "raw_output": raw_output
        }

    # Save in new location: outputs/scripts/script_<id>.json
    scripts_dir = os.path.join(OUTPUT_DIR, "scripts")
    os.makedirs(scripts_dir, exist_ok=True)

    filepath = os.path.join(scripts_dir, f"script_{TITLE_ID}.json")

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(script_data, f, indent=2, ensure_ascii=False)

    print(f"Script saved at: {filepath}")
    return filepath
