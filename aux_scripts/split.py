import os
import subprocess

# === CONFIGURATION ===
input_video = "input.mp4"
cut_time = 1.36
output_part1 = "part1.mp4"
output_part2 = "part2.mp4"

if not os.path.exists(input_video):
    raise FileNotFoundError(f"❌ Input file not found: {input_video}")

print(f"🔪 Splitting '{input_video}' safely at {cut_time} s...")

# --- Part 1: from start → cut_time ---
cmd1 = [
    "ffmpeg", "-y",
    "-i", input_video,
    "-t", str(cut_time),
    "-c:v", "libx264", "-crf", "18", "-preset", "slow",
    "-c:a", "aac", "-b:a", "192k",
    output_part1
]

# --- Part 2: from cut_time → end ---
cmd2 = [
    "ffmpeg", "-y",
    "-ss", str(cut_time),
    "-i", input_video,
    "-c:v", "libx264", "-crf", "18", "-preset", "slow",
    "-c:a", "aac", "-b:a", "192k",
    output_part2
]

subprocess.run(cmd1)
subprocess.run(cmd2)

print(f"✅ Done!\n   • {output_part1}\n   • {output_part2}")
