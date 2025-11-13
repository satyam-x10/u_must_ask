# generate_clips.py

import os
import json
from moviepy.editor import ImageClip, AudioFileClip


def generate_scene_clip(image_path: str, audio_path: str, output_path: str):
    """Create a video from an image and an audio file, applying random cinematic effects."""
    audio_clip = AudioFileClip(audio_path)
    duration = audio_clip.duration

    # Base image clip
    image_clip = ImageClip(image_path, duration=duration)

    # Combine with audio
    video_clip = image_clip.set_audio(audio_clip)

    # Export the video
    video_clip.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")

    # Cleanup
    video_clip.close()
    image_clip.close()
    audio_clip.close()

