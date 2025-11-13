import os
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip

# ---------- CONFIG ----------
SCRIPT_PATH = "script.json"
OUTPUT_PATH = "outputs/titlecard.mp4"
FINAL_SIZE = (1920, 1080)   # Full HD 16:9
DURATION = 1.0               # seconds
BG_COLOR = (10, 10, 10)      # dark background
TEXT_COLOR = "white"
FONT_SIZE = 72
# ----------------------------


# === Load script title ===
with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
    script = json.load(f)

title = script.get("title", "Untitled Video").strip()
print(f"🎬 Creating title card for: “{title}”")

# === Generate image ===
img = Image.new("RGB", FINAL_SIZE, BG_COLOR)
draw = ImageDraw.Draw(img)

# Load font
try:
    font = ImageFont.truetype("arial.ttf", FONT_SIZE)
except Exception:
    font = ImageFont.load_default()

# Measure text size and position it dead center
text_w = draw.textlength(title, font=font)
text_h = font.getbbox(title)[3] - font.getbbox(title)[1]
x = (FINAL_SIZE[0] - text_w) // 2
y = (FINAL_SIZE[1] - text_h) // 2

draw.text((x, y), title, font=font, fill=TEXT_COLOR)

# Convert to clip
np_img = np.array(img)
clip = ImageClip(np_img).set_duration(DURATION)

# === Export ===
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
clip.write_videofile(
    OUTPUT_PATH,
    codec="libx264",
    audio=False,
    fps=30
)

print(f"✅ Title card exported: {OUTPUT_PATH}")
