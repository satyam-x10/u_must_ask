import cv2
from rembg import remove
from PIL import Image
import numpy as np
from tqdm import tqdm
import os
import subprocess

# --- Input / output setup ---
input_video = "student/s1.mp4"
temp_dir = "temp_frames"
output_video = "student/s1_nobg.webm"  # .webm supports transparency with VP9

os.makedirs(temp_dir, exist_ok=True)

# --- Read video ---
cap = cv2.VideoCapture(input_video)
fps = cap.get(cv2.CAP_PROP_FPS)
frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

print(f"Total frames: {frame_count}, Resolution: {width}x{height}, FPS: {fps:.2f}")

# --- Process frames ---
for i in tqdm(range(frame_count), desc="Removing background"):
    ret, frame = cap.read()
    if not ret:
        break

    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    output = remove(img)  # remove background

    # Convert back to OpenCV RGBA for video writing
    rgba = cv2.cvtColor(np.array(output), cv2.COLOR_RGBA2BGRA)
    cv2.imwrite(f"{temp_dir}/frame_{i:04d}.png", rgba)

cap.release()

# --- Use FFmpeg to combine frames into video (with alpha channel) ---
ffmpeg_exe = r"C:\Users\satyam\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0-full_build\bin\ffmpeg.exe"

cmd = [
    ffmpeg_exe,
    "-framerate", str(fps),
    "-i", os.path.join(temp_dir, "frame_%04d.png"),
    "-c:v", "libvpx-vp9",
    "-pix_fmt", "yuva420p",   # preserve transparency
    "-lossless", "1",         # full quality
    "-y",
    output_video
]

print("\n🎞️ Combining frames into final video...")
subprocess.run(cmd, check=True)
print(f"✅ Done! Saved as {output_video}")

# Optional cleanup
import shutil
shutil.rmtree(temp_dir)
