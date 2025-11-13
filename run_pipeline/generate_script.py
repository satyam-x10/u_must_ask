import re
import json
import os
from llm.generate_script import generate_script
from scripts.prompt import build_script_prompt

OUTPUT_DIR = "outputs"

def generate_Script_Gemini(TITLE_NAME, TITLE_ID):
    """
    Generates a Gemini-based JSON script and saves it under:
    outputs/<TITLE_ID>/script.json
    Creates folders automatically if missing.
    """
    # Ensure base outputs folder exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Build the full prompt
    full_prompt = build_script_prompt(TITLE_NAME)

    # === Generate script ===
    raw_output = generate_script(full_prompt)

    # === Clean and extract JSON ===
    cleaned = raw_output.strip()
    cleaned = re.sub(r"^```(?:json)?|```$", "", cleaned.strip(), flags=re.MULTILINE).strip()

    # Try to extract only the JSON block
    json_match = re.search(r"\{[\s\S]*\}", cleaned)
    if json_match:
        cleaned = json_match.group(0)

    # === Try parsing JSON ===
    try:
        result = json.loads(cleaned)
    except json.JSONDecodeError as e:
        print("⚠️ Gemini returned malformed JSON. Saving raw output for review.")
        result = {"raw_output": raw_output, "error": str(e)}

    # === Prepare output folder and file ===
    title_folder = os.path.join(OUTPUT_DIR, str(TITLE_ID))
    os.makedirs(title_folder, exist_ok=True)  # ✅ ensure outputs/<TITLE_ID>/ exists

    filepath = os.path.join(title_folder, "script.json")

    # === Save JSON ===
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"✅ Script saved to {filepath}")

    return filepath
