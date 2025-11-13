import os
import subprocess

# ---------- CONFIG ----------
AUDIO_DIR = "outputs/audio"
VIDEO_DIR = "outputs/video_silent"
TEMP_DIR = "outputs/temp_merged"
FINAL_DIR = "outputs/final"
FINAL_FILE = os.path.join(FINAL_DIR, "conversation.mp4")
# ----------------------------

os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(FINAL_DIR, exist_ok=True)


def get_sorted_files(folder, ext):
    """Return numerically sorted file list."""
    files = [f for f in os.listdir(folder) if f.lower().endswith(ext)]
    files.sort(key=lambda x: int("".join(filter(str.isdigit, x)) or 0))
    return files


def merge_audio_video(video_path, audio_path, output_path):
    """Force mux a wav + mp4 -> mp4 with AAC audio"""
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", audio_path,
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        output_path
    ]
    subprocess.run(cmd, check=True)


def main():
    audio_files = get_sorted_files(AUDIO_DIR, ".wav")
    video_files = get_sorted_files(VIDEO_DIR, ".mp4")
    num = min(len(audio_files), len(video_files))

    if num == 0:
        print("❌ No matching audio/video pairs found.")
        return

    print(f"🎬 Found {num} pairs to merge")

    # Step 1: merge each pair individually
    merged_names = []
    for i in range(num):
        a = os.path.join(AUDIO_DIR, audio_files[i])
        v = os.path.join(VIDEO_DIR, video_files[i])
        merged_name = f"merged_{i+1}.mp4"
        merged_path = os.path.join(TEMP_DIR, merged_name)
        print(f"🔊 Merging {i}th files")
        merge_audio_video(v, a, merged_path)
        merged_names.append(merged_name)

    # Step 2: build list.txt for concat
    list_path = os.path.join(TEMP_DIR, "list.txt")
    with open(list_path, "w", encoding="utf-8") as f:
        for name in merged_names:
            f.write(f"file '{name}'\n")

    # Step 3: concatenate using FFmpeg
    print("\n🧩 Concatenating final video...")
    subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", "list.txt",
        "-c", "copy",
        os.path.abspath(FINAL_FILE)
    ], cwd=TEMP_DIR, check=True)

    print(f"\n✅ Final video created with audio: ")


if __name__ == "__main__":
    main()
