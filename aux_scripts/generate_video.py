# --- FIX for Pillow compatibility ---
import PIL.Image
if not hasattr(PIL.Image, "ANTIALIAS"):
    PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS

import os
import json
import random
import numpy as np
from tqdm import tqdm
from moviepy.editor import (
    VideoFileClip,
    concatenate_videoclips,
    CompositeVideoClip,
    AudioFileClip,
    ImageClip
)
from PIL import Image, ImageDraw, ImageFont

def create_pillow_caption(text, width, height, duration, fontsize=38):
    """Creates a subtitle overlay using Pillow + MoviePy."""
    img = Image.new("RGBA", (width, 120), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", fontsize)
    except:
        font = ImageFont.load_default()

    # Word wrapping
    max_width = int(width * 0.9)
    lines = []
    words = text.split()
    line = ""
    for word in words:
        if draw.textlength(line + " " + word, font=font) <= max_width:
            line += " " + word
        else:
            lines.append(line.strip())
            line = word
    lines.append(line.strip())

    y_text = 10
    for line in lines:
        line_width = draw.textlength(line, font=font)
        x = (width - line_width) // 2
        draw.text((x, y_text), line, font=font, fill="white",
                  stroke_width=2, stroke_fill="black")
        y_text += fontsize + 5

    np_frame = np.array(img)
    clip = ImageClip(np_frame).set_duration(duration)
    clip = clip.set_position(("center", height - 140))
    return clip


def apply_pan_zoom_effect(image_path, duration, width=1920, height=1080):
    """Applies a random Ken Burns (pan/zoom) effect to a static image."""
    zoom_start = random.uniform(1.0, 1.05)
    zoom_end = random.uniform(1.08, 1.15)
    pan_x = random.choice(["left", "right", "center"])
    pan_y = random.choice(["top", "bottom", "center"])

    img_clip = ImageClip(image_path, duration=duration)
    img_clip = img_clip.resize(height=height * zoom_start)

    def zoom(t):
        zoom_factor = zoom_start + (zoom_end - zoom_start) * (t / duration)
        return zoom_factor

    def position(t):
        z = zoom(t)
        dx = dy = 0
        if pan_x == "left":
            dx = 0
        elif pan_x == "right":
            dx = width - width / z
        else:
            dx = (width - width / z) / 2

        if pan_y == "top":
            dy = 0
        elif pan_y == "bottom":
            dy = height - height / z
        else:
            dy = (height - height / z) / 2

        return (-dx, -dy)

    return img_clip.fl_time(lambda t: t).resize(lambda t: zoom(t)).set_position(position)


# ---------- CONFIG ----------
CONFIG_PATH = "config.json"
SCRIPT_PATH = "script.json"
AUDIO_DIR = "outputs/audio"
SCENE_DIR = "outputs/scenes"
OUTPUT_VIDEO = "outputs/final_video.mp4"
# ----------------------------

# === Load config ===
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = json.load(f)

animations = config.get("pip", {})

# === Load main script ===
with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
    script_data = json.load(f)

scenes = script_data["scenes"]
clips = []

os.makedirs(os.path.dirname(OUTPUT_VIDEO), exist_ok=True)

print(f"🎬 Found animations: {list(animations.keys())}")
print(f"🎧 Using pre-generated audio from: {AUDIO_DIR}")

# === Build scenes ===
for idx, scene in enumerate(tqdm(scenes, desc="Compositing scenes")):
    text = scene["text"].strip()
    scene_image = os.path.join(SCENE_DIR, scene["scene"])
    duration = scene.get("duration", None)
    audio_path = os.path.join(AUDIO_DIR, f"scene_{idx+1:03d}.wav")

    if not os.path.exists(scene_image):
        raise FileNotFoundError(f"Missing scene image: {scene_image}")
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Missing audio: {audio_path}")

    audio_clip = AudioFileClip(audio_path)
    duration = duration or audio_clip.duration

    # Add pan & zoom effect
    img_clip = apply_pan_zoom_effect(scene_image, duration)

    # Add caption
    caption = create_pillow_caption(text, 1920, 1080, duration)

    # Combine visuals and audio
    composite = CompositeVideoClip([img_clip, caption]).set_audio(audio_clip)
    clips.append(composite)

# Combine all scenes
final_video = concatenate_videoclips(clips, method="compose").fadeout(1.5)

# Export
final_video.write_videofile(
    OUTPUT_VIDEO,
    codec="libx264",
    audio_codec="aac",
    fps=30,
    threads=4
)

print(f"✅ Final video saved: {OUTPUT_VIDEO}")
