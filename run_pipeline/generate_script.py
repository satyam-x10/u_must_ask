import re
import json
import os
from json_repair import repair_json
from llm.generate_script import generate_script
from scripts.prompt import build_script_prompt

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
    prompt = build_script_prompt(TITLE_NAME)

    script_data = None
    raw_output = ""

    for attempt in range(1, MAX_RETRIES + 1):

        print(f"\n🔄 Attempt {attempt}/{MAX_RETRIES} for ID {TITLE_ID}")

        raw_output = generate_script(prompt)

        # Remove markdown code fences
        cleaned = re.sub(r"```(?:json)?|```", "", raw_output).strip()

        # Extract potential JSON
        block = extract_first_json_block(cleaned)
        if not block:
            print("❌ No JSON block. Retrying...")
            continue

        # Try normal json first
        try:
            script_data = json.loads(block)
        except:
            # Try repairing JSON
            try:
                repaired = repair_json(block)
                script_data = json.loads(repaired)
                print("🔧 JSON repaired successfully.")
            except:
                print("❌ JSON unrecoverable. Retrying...")
                continue

        # Validate structure
        if "scenes" not in script_data:
            print("❌ 'scenes' missing. Retrying...")
            continue

        if not isinstance(script_data["scenes"], list) or len(script_data["scenes"]) < 10:
            print("❌ Invalid scenes array. Retrying...")
            continue

        # SUCCESS
        print("✅ Valid script generated.")
        break

    # ---------------------------------------
    # Final fallback if totally invalid
    # ---------------------------------------
    if script_data is None:
        script_data = {
            "error": "Failed to generate valid script after retries.",
            "raw_output": raw_output
        }

    # Save output
    title_folder = os.path.join(OUTPUT_DIR, str(TITLE_ID))
    os.makedirs(title_folder, exist_ok=True)

    filepath = os.path.join(title_folder, "script.json")

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(script_data, f, indent=2, ensure_ascii=False)

    print(f"📄 Script saved at: {filepath}")
    return filepath
