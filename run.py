# from run_pipeline.generate_script import generate_Script_Gemini
# from run_pipeline.generate_images import generate_images
# from run_pipeline.generate_audios import generate_audios
# from scripts.tts_env import activate_ttsenv, deactivate_ttsenv
# from run_pipeline.generate_intros_outros import generate_intros_outros
from run_pipeline.generate_all_clips import generate_all_clips
# from run_pipeline.generate_thumbnails import generate_thumbnails
from run_pipeline.generate_final_video import generate_final_video

import json
import os

# =====================================================
# USER INPUT: Process titles from START → END
# =====================================================

START_ID = 1
END_ID = 1

# Load the titles file
with open("static/titles.json", "r", encoding="utf-8") as f:
    TITLE_DATA = json.load(f)

def get_title_data(title_id: str):
    """Return (title, prompt) for given title_id"""
    for item in TITLE_DATA:
        if item["id"] == title_id:
            return item["title"], item.get("prompt")
    return None, None


# =====================================================
# MAIN LOOP – PROCESS ALL TITLES
# =====================================================

for tid in range(START_ID, END_ID + 1):

    TITLE_ID = str(tid)
    TITLE_NAME, TITLE_PROMPT = get_title_data(TITLE_ID)

    if not TITLE_NAME:
        print(f"❌ Title ID {TITLE_ID} not found. Skipping.")
        continue

    print("\n====================================")
    print(f"▶ Processing Title ID: {TITLE_ID}")
    print("TITLE_NAME:", TITLE_NAME)
    print("TITLE_PROMPT:", TITLE_PROMPT)
    print("====================================\n")

    # -------------------------------------
    # 1) Generate script
    # -------------------------------------
    # generate_Script_Gemini(TITLE_NAME, TITLE_ID)

    # Overwrite to ensure correct path format
    script_path = f"outputs/scripts/script_{TITLE_ID}.json"

    # -------------------------------------
    # 2) Generate audios
    # -------------------------------------
    # generate_audios(script_path)

    # generate_images(script_path)


    # -------------------------------------
    # 4) Merge image + audio into clips (optional)
    # -------------------------------------
    generate_all_clips(script_path)

    #  generate intro and outro clip
    # generate_intros_outros(TITLE_ID)


    # generate_thumbnails(TITLE_ID, TITLE_NAME)
    # -------------------------------------
    # 6) Merge all clips into one final video (optional)
    # -------------------------------------
    final_video_path = generate_final_video(script_path)

print("\n✅ ALL TITLES PROCESSED SUCCESSFULLY!")
