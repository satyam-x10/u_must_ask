import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip

# ---------- CONFIG ----------
OUTPUT_PATH = "outputs/thankyou.mp4"
FINAL_SIZE = (1920, 1080)   # Full HD
DURATION = 1.0               # seconds
BG_COLOR = (10, 10, 10)      # dark background
TEXT_COLOR = "white"
FONT_SIZE = 72
TEXT = "Thank you for watching!"
# ----------------------------

# === Create image ===
img = Image.new("RGB", FINAL_SIZE, BG_COLOR)
draw = ImageDraw.Draw(img)

# Load font
try:
    font = ImageFont.truetype("arial.ttf", FONT_SIZE)
except Exception:
    font = ImageFont.load_default()

# Measure text
text_w = draw.textlength(TEXT, font=font)
text_h = font.getbbox(TEXT)[3] - font.getbbox(TEXT)[1]
x = (FINAL_SIZE[0] - text_w) // 2
y = (FINAL_SIZE[1] - text_h) // 2

# Draw text
draw.text((x, y), TEXT, font=font, fill=TEXT_COLOR)

# Convert to movie clip
np_img = np.array(img)
clip = ImageClip(np_img).set_duration(DURATION)

# === Export video ===
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
clip.write_videofile(
    OUTPUT_PATH,
    codec="libx264",
    audio=False,
    fps=30
)

print(f"✅ Thank-you card exported: {OUTPUT_PATH}")
