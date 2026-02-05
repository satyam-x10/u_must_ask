import os
import json
import time
from scripts.vits import generate_tts_audio
from pydub import AudioSegment
# from scripts.bark import generate_tts_audio


def generate_audios(filepath: str) -> list:

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    # Read JSON
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "scenes" not in data:
        raise ValueError("Invalid JSON format — missing scenes key")

    title = data.get("title", "Untitled Project")
    scenes = data["scenes"]

    # Extract script ID
    filename = os.path.basename(filepath)
    script_id = filename.replace("script_", "").replace(".json", "")

    audio_dir = os.path.join("outputs", "audios", script_id)
    os.makedirs(audio_dir, exist_ok=True)

    print(f"\nGenerating FULL audio for {title} with {len(scenes)} scenes\n")

    full_audio = AudioSegment.empty()

    # ----------------------------------------
    # OPTIONAL INTRO (inline)
    # ----------------------------------------
    # intro_text = title
    # try:
    #     intro_path = os.path.join(audio_dir, "__intro_tmp.wav")
    #     generate_tts_audio(intro_text, intro_path, "excited")
    #     full_audio += AudioSegment.from_wav(intro_path)
    #     os.remove(intro_path)
    # except Exception as e:
    #     print(f"Intro skipped {e}")

    # ----------------------------------------
    # SCENES (single pass)
    # ----------------------------------------
    for scene in scenes:
        scene_id = scene.get("id")
        text = scene.get("text", "").strip()
        emotion = scene.get("emotion", "neutral")
        delay_sec = scene.get("audio_delay", 0.5)

        if not text:
            print(f"Scene {scene_id} empty skipping")
            continue

        # Delay BEFORE scene
        if delay_sec > 0:
            full_audio += AudioSegment.silent(duration=int(delay_sec * 1000))

        # We MUST save this file for the video generation step (to know duration)
        filename = f"scene_{scene_id}.wav"
        scene_path = os.path.join(audio_dir, filename)

        try:
            generate_tts_audio(text, scene_path, emotion)
            full_audio += AudioSegment.from_wav(scene_path)
            # Do NOT remove it. interactive_clip.py needs it.
        except Exception as e:
            print(f"Scene {scene_id} failed {e}")
        # finally:
        #     if os.path.exists(tmp_path):
        #         os.remove(tmp_path)

    # ----------------------------------------
    # OPTIONAL OUTRO (inline)
    # ----------------------------------------
    # outro_text = "Thank you for watching make sure to subscribe for more"
    # try:
    #     outro_path = os.path.join(audio_dir, "__outro_tmp.wav")
    #     generate_tts_audio(outro_text, outro_path, "calm")
    #     full_audio += AudioSegment.from_wav(outro_path)
    #     os.remove(outro_path)
    # except Exception as e:
    #     print(f"Outro skipped {e}")

    # ----------------------------------------
    # EXPORT FINAL
    # ----------------------------------------
    full_audio_path = os.path.join(audio_dir, "full_audio.wav")
    full_audio.export(full_audio_path, format="wav")

    print(f"\nFull audio generated at {full_audio_path}")

    return [full_audio_path]
