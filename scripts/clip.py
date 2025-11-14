import os
import json
import random
from moviepy.editor import ImageClip, AudioFileClip


def generate_scene_clip(image_path: str, audio_path: str, output_path: str):
    """Create a video from an image and an audio file with independent random fade effects."""

    audio = AudioFileClip(audio_path)
    duration = audio.duration

    clip = ImageClip(image_path, duration=duration)

    # -----------------------------
    # Fade-in (30% chance)
    # -----------------------------
    if random.random() < 0.30:
        fade_in_dur = random.uniform(0.3, 1.0)
        clip = clip.fadein(fade_in_dur)

    # -----------------------------
    # Fade-out (30% chance)
    # -----------------------------
    if random.random() < 0.30:
        fade_out_dur = random.uniform(0.3, 1.0)
        clip = clip.fadeout(fade_out_dur)

    # -----------------------------
    # Add audio + export
    # -----------------------------
    clip = clip.set_audio(audio)

    clip.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")

    clip.close()
    audio.close()
