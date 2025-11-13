import os
import subprocess
from tqdm import tqdm

# --- Verified FFmpeg path ---
ffmpeg_exe = r"C:\Users\satyam\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0-full_build\bin\ffmpeg.exe"

# --- Input and output folders ---
input_dir = "student"         # Folder containing source videos
output_dir = "inverted_videos"   # Folder for inverted videos
os.makedirs(output_dir, exist_ok=True)

# --- Supported video formats ---
video_exts = (".webm", ".mov", ".mp4", ".mkv")

for filename in os.listdir(input_dir):
    if not filename.lower().endswith(video_exts):
        continue

    input_path = os.path.join(input_dir, filename)
    name, ext = os.path.splitext(filename)
    output_path = os.path.join(output_dir, f"{name}_inverted{ext}")

    # --- FFmpeg command ---
    cmd = [
        ffmpeg_exe,
        "-i", input_path,
        "-vf", "lutrgb=r=negval:g=negval:b=negval",
        "-c:v", "libvpx-vp9",
        "-pix_fmt", "yuva420p",
        "-y",  # overwrite output
        output_path
    ]

    print(f"\n🎞️ Inverting: {filename}")
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    print(f"✅ Inverted with transparency: {output_path}")

print("\n🎉 All videos processed successfully!")
