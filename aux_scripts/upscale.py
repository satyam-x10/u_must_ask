import os
import subprocess

input_video = "video.mp4"
cut_time = 1.36
output_part1 = "part1.mp4"
output_part2 = "part2.mp4"

if not os.path.exists(input_video):
    raise FileNotFoundError(f"❌ File not found: {input_video}")

print(f"🔪 Splitting '{input_video}' at {cut_time} seconds...")

# --- Part 1 (fast copy, no quality loss) ---
cmd1 = [
    "ffmpeg", "-y", "-i", input_video,
    "-t", str(cut_time),
    "-c", "copy",
    output_part1
]

# --- Part 2 (re-encode to avoid corruption) ---
cmd2 = [
    "ffmpeg", "-y", "-ss", str(cut_time), "-i", input_video,
    "-c:v", "libx264", "-crf", "18", "-preset", "slow",  # visually lossless
    "-c:a", "copy",
    output_part2
]

subprocess.run(cmd1, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
subprocess.run(cmd2, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

print(f"✅ Done!")
print(f"   • First part → {output_part1} (lossless copy)")
print(f"   • Second part → {output_part2} (re-encoded, same quality)")
