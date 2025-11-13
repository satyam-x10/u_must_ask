import PIL.Image
if not hasattr(PIL.Image, "ANTIALIAS"):
    PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS

import os
import json
import numpy as np
from moviepy.editor import VideoFileClip, CompositeVideoClip, AudioFileClip, ImageClip
from PIL import Image, ImageDraw, ImageFont

# ---------- CONFIG ----------
CONFIG_PATH = "config.json"
SCRIPT_PATH = "script.json"
AUDIO_DIR = "outputs/audio"
OUTPUT_PATH = "outputs/outro.mp4"
FINAL_SIZE = (1920, 1080)  # Full HD 16:9

# --- Tuned PIP motion (mirrored) ---
START_SCALE = 0.3
END_SCALE = 0.9
X_START_RATIO = 0.12         # same as intro's final pos
Y_START_RATIO = 0.82
MOVE_PORTION = 0.4
CAPTION_BOTTOM_OFFSET = 220  # keep caption clear
# ----------------------------


def create_caption(text, width, height, duration, delay=0, fontsize=42):
    """Generate subtitle text with start delay."""
    img = Image.new("RGBA", (width, 180), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", fontsize)
    except Exception:
        font = ImageFont.load_default()

    # Word wrapping
    words, lines, line = text.split(), [], ""
    for w in words:
        if draw.textlength(line + " " + w, font=font) <= width * 0.9:
            line += " " + w
        else:
            lines.append(line.strip())
            line = w
    lines.append(line.strip())

    y = 10
    for l in lines:
        tw = draw.textlength(l, font=font)
        x = (width - tw) // 2
        draw.text((x, y), l, font=font, fill="white",
                  stroke_width=2, stroke_fill="black")
        y += fontsize + 4

    np_img = np.array(img)
    clip = ImageClip(np_img).set_duration(duration - delay)
    clip = clip.set_start(delay)
    clip = clip.set_position(("center", height - CAPTION_BOTTOM_OFFSET))
    return clip


# === Load configuration ===
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = json.load(f)
animations = config["pip"]

with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
    script = json.load(f)

scene = script["scenes"][-1]  # last scene (bye)
anim_path = animations.get(scene["animation"])
if not anim_path or not os.path.exists(anim_path):
    raise FileNotFoundError(f"Missing animation: {scene['animation']}")

# === Load audio ===
scene_index = len(script["scenes"])
audio_path = os.path.join(AUDIO_DIR, f"scene_{scene_index:03d}.wav")
if not os.path.exists(audio_path):
    raise FileNotFoundError(f"Audio not found for outro: {audio_path}")

audio_clip = AudioFileClip(audio_path)
audio_duration = audio_clip.duration
TOTAL_DURATION = audio_duration
print(f"🎧 Audio: {audio_duration:.2f}s | Total: {TOTAL_DURATION:.2f}s")

# === Load animation ===
video_clip = VideoFileClip(anim_path).loop(duration=TOTAL_DURATION)
clip_w, clip_h = video_clip.size


# === Smooth easing ===
def ease_out_cubic(x):
    return 1 - (1 - x) ** 3


# === Motion (mirrored) ===
def scale_at_time(t):
    progress = min(t / (TOTAL_DURATION * MOVE_PORTION), 1)
    eased = ease_out_cubic(progress)
    return START_SCALE + (END_SCALE - START_SCALE) * eased


def pos_at_time(t):
    W, H = FINAL_SIZE
    x_start, y_start = W * X_START_RATIO, H * Y_START_RATIO
    x_end, y_end = W / 2, H / 2
    progress = min(t / (TOTAL_DURATION * MOVE_PORTION), 1)
    eased = ease_out_cubic(progress)
    cx = x_start + (x_end - x_start) * eased
    cy = y_start + (y_end - y_start) * eased
    scaled_w = clip_w * scale_at_time(t)
    scaled_h = clip_h * scale_at_time(t)
    return (cx - scaled_w / 2, cy - scaled_h / 2)


# === Build moving PIP ===
moving_clip = (
    video_clip.set_duration(TOTAL_DURATION)
    .resize(lambda t: scale_at_time(t))
    .set_position(lambda t: pos_at_time(t))
)

# === Caption ===
caption = create_caption(scene["text"], *FINAL_SIZE,
                         duration=TOTAL_DURATION,
                         delay=0)

# === Final Composite ===
final = CompositeVideoClip([moving_clip, caption],
                           size=FINAL_SIZE).set_audio(audio_clip)

os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
final.write_videofile(
    OUTPUT_PATH,
    codec="libx264",
    audio_codec="aac",
    fps=30,
    threads=4
)

print(f"✅ Outro exported successfully: {OUTPUT_PATH}")
