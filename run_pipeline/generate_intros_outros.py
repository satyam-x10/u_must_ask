import json
import os
from scripts.intro_outro import  generate_intro_clip , generate_outro_clip

def generate_intros_outros(TITLE_ID: str):
    # Load titles.json
    with open("static/titles.json", "r", encoding="utf-8") as f:
        titles = json.load(f)

    # Find the title for this ID
    title_obj = next((t for t in titles if t["id"] == TITLE_ID), None)
    if not title_obj:
        raise ValueError(f"Title ID {TITLE_ID} not found in titles.json")

    title_text = title_obj["title"]

    # Paths
    base_dir = f"outputs"
    thumb_path = f"{base_dir}/thumbnails/thumb_{TITLE_ID}.png"

    intro_audio = f"{base_dir}/audios/{TITLE_ID}/intro.wav"
    outro_audio = f"{base_dir}/audios/{TITLE_ID}/outro.wav"

    save_intro = f"outputs/clips/{TITLE_ID}/intro.mp4"
    save_outro = f"outputs/clips/{TITLE_ID}/outro.mp4"

    os.makedirs(f"outputs/clips/{TITLE_ID}", exist_ok=True)

    # Generate 2-sec intro
    intro_clip = generate_intro_clip(
        image_path=thumb_path,
        audio_path=intro_audio,
        title_text=title_text,
        )
    intro_clip.write_videofile(save_intro, fps=30, codec="libx264", audio_codec="aac")

    # Generate 2-sec outro (no text)
    outro_clip = generate_outro_clip(
        audio_path=outro_audio,
    )
    outro_clip.write_videofile(save_outro, fps=30, codec="libx264", audio_codec="aac")

    return save_intro, save_outro
