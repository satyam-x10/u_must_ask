import os
import cv2
import numpy as np
import imageio
from PIL import Image
from tqdm import tqdm

# === CONFIGURATION ===
input_dir = "frames/idle/"     # folder containing PNGs
output_video = "idle.webm"  # use webm for transparent output
fps = 30  # smooth playback

# === LOAD FILES ===
files = sorted([f for f in os.listdir(input_dir) if f.lower().endswith(".png")])
if not files:
    raise ValueError("❌ No PNG files found in the input directory!")

# === READ FIRST FRAME ===
first_frame = Image.open(os.path.join(input_dir, files[0])).convert("RGBA")
width, height = first_frame.size

# === CREATE WRITER (VP9 for alpha transparency) ===
writer = imageio.get_writer(
    output_video,
    fps=fps,
    codec="libvpx-vp9",
    pixelformat="yuva420p",  # keeps transparency
    quality=8
)

print(f"🕊️ Merging {len(files)} frames ({width}x{height}) into {output_video}")

# === WRITE FRAMES ===
for f in tqdm(files, desc="Merging frames"):
    frame_path = os.path.join(input_dir, f)
    img = Image.open(frame_path).convert("RGBA")
    arr = np.array(img)
    writer.append_data(arr)

writer.close()
print(f"\n✅ Done! Saved transparent video to: {output_video}")
print("💡 Tip: Use .webm for web/video compositing or .mov (ProRes) for video editors.")
