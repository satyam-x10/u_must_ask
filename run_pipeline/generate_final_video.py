import os
from moviepy.editor import VideoFileClip, concatenate_videoclips


def generate_final_video(base_dir: str):
    """
    Merges all clips inside <base_dir>/clips into a single final video.
    Output is saved as <base_dir>/final_video.mp4
    """

    # Handle if user passed script.json path instead of folder
    if base_dir.endswith("script.json"):
        base_dir = os.path.dirname(base_dir)

    clips_dir = os.path.join(base_dir, "clips")
    output_path = os.path.join(base_dir, "final_video.mp4")

    # Get all scene clips (sorted by scene number)
    video_files = sorted(
        [os.path.join(clips_dir, f) for f in os.listdir(clips_dir) if f.endswith((".mp4", ".mkv"))]
    )

    if not video_files:
        print(f"⚠️ No video clips found in {clips_dir}")
        return

    print(f"🎬 Found {len(video_files)} clips. Merging...")

    # Load and concatenate all clips
    clips = [VideoFileClip(vf) for vf in video_files]
    final_video = concatenate_videoclips(clips, method="compose")

    # Write output file
    final_video.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=24)

    # Cleanup
    for clip in clips:
        clip.close()
    final_video.close()

    print(f"✅ Final video saved at: {output_path}")
    return output_path
