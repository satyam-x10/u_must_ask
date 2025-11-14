import os
from moviepy.editor import VideoFileClip, concatenate_videoclips

def generate_final_video(filepath_to_script: str):
    """
    Example:
        filepath_to_script = "outputs/scripts/script_11.json"

    Loads clips from:
        outputs/clips/11/

    Saves final video to:
        outputs/videos/11.mp4
    """

    # Extract ID from filename
    filename = os.path.basename(filepath_to_script)          # script_11.json
    script_id = filename.replace("script_", "").replace(".json", "")  # 11

    BASE = "outputs"

    clips_dir = os.path.join(BASE, "clips", script_id)
    videos_dir = os.path.join(BASE, "videos")
    os.makedirs(videos_dir, exist_ok=True)

    # New desired output path (no folder)
    output_path = os.path.join(videos_dir, f"{script_id}.mp4")

    # Collect clip files
    if not os.path.exists(clips_dir):
        print(f"No clips directory found: {clips_dir}")
        return None

    video_files = sorted([
        os.path.join(clips_dir, f)
        for f in os.listdir(clips_dir)
        if f.endswith((".mp4", ".mkv"))
    ])

    if not video_files:
        print(f"No video files found in: {clips_dir}")
        return None

    print(f"Merging {len(video_files)} clips...")

    clips = [VideoFileClip(vf) for vf in video_files]
    final_video = concatenate_videoclips(clips, method="compose")

    final_video.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=24)

    # Cleanup
    for clip in clips:
        clip.close()
    final_video.close()

    print(f"Final video saved at: {output_path}")
    return output_path
