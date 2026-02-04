import random
import textwrap
import subprocess
import os
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip


def split_text_by_time(text: str, audio_duration: float, max_chars=40):
    wrapped = textwrap.wrap(text, max_chars)
    if not wrapped:
        return []
    segment = audio_duration / len(wrapped)
    result = []
    t = 0
    for line in wrapped:
        result.append((line, t, t + segment))
        t += segment
    return result


def create_caption_image(text, width, fontsize=34, min_fontsize=34):
    # Render at 3x resolution for extreme sharpness
    scale = 3

    # Increase base font size slightly for "bigger" look
    fontsize = int(fontsize * 1.3)
    min_fontsize = int(min_fontsize * 1.3)

    final_height = 50  # Increased height for bigger text
    W = width * scale
    H = final_height * scale

    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    def load_ttf(size):
        # Try to find a Bold font variant
        for f in ["arialbd.ttf", "arial.ttf", "DejaVuSans-Bold.ttf", "DejaVuSans.ttf"]:
            try:
                return ImageFont.truetype(f, size)
            except:
                pass
        raise RuntimeError("Missing TTF font — install arial or dejavu.")

    fs = fontsize * scale
    font = load_ttf(fs)

    # Shrink font if wider than allowed
    while draw.textlength(text, font=font) > W - (20 * scale) and fs > min_fontsize * scale:
        fs -= scale
        font = load_ttf(fs)

    ascent, descent = font.getmetrics()
    text_h = ascent + descent
    text_w = draw.textlength(text, font=font)
    
    y = (H - text_h) // 2
    x = (W - text_w) // 2
    
    # Draw White Background (with some padding)
    padding = 10 * scale
    bg_box = [
        x - padding, 
        y - padding/2, 
        x + text_w + padding, 
        y + text_h + padding/2
    ]
    draw.rectangle(bg_box, fill=(255, 255, 255, 255))

    # Draw Black Text (Bolder if font supported it, otherwise just black)
    draw.text(
        (x, y),
        text,
        font=font,
        fill=(0, 0, 0, 255),
        stroke_width=0, 
    )

    img = img.resize((width, final_height), Image.LANCZOS)

    return np.array(img)


def generate_scene_clip(image_path: str, audio_path: str, output_path: str, audio_text: str):
    audio = AudioFileClip(audio_path)
    duration = audio.duration
    
    # Force audio to exact frame boundary to prevent padding issues
    fps = 24
    exact_duration = int(duration * fps) / fps
    audio = audio.subclip(0, exact_duration)
    duration = exact_duration

    clip = ImageClip(image_path, duration=duration)
    clip = clip.resize(newsize=(1920, 1080))

    if random.random() < 0.30:
        clip = clip.fadein(random.uniform(0.3, 1.0))
    if random.random() < 0.30:
        clip = clip.fadeout(random.uniform(0.3, 1.0))

    subtitles = split_text_by_time(audio_text, duration, max_chars=42)
    subtitle_clips = []

    for text, start, end in subtitles:
        img = create_caption_image(text, clip.w)
        txt = (
            ImageClip(img, transparent=True)
            .set_position(("center", 10))
            .set_start(start)
            .set_end(end)
        )
        subtitle_clips.append(txt)

    final = CompositeVideoClip([clip] + subtitle_clips, size=clip.size)
    
    # Create temp video without audio first
    temp_video = output_path.replace(".mp4", "_temp.mp4")
    
    # Write video only (no audio processing by MoviePy)
    final.write_videofile(
        temp_video,
        fps=24,
        codec="libx264",
        audio=False,
        preset='medium',
        threads=4,
        logger=None
    )
    
    # Mux original clean audio with ffmpeg directly
    subprocess.run([
        "ffmpeg", "-y",
        "-i", temp_video,
        "-i", audio_path,
        "-c:v", "copy",  # Don't re-encode video
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",  # Stop at shortest stream
        "-avoid_negative_ts", "make_zero",  # Prevent audio sync issues
        output_path
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Cleanup
    os.remove(temp_video)
    clip.close()
    audio.close()


# Alternative version if you want to keep MoviePy audio handling
def generate_scene_clip_moviepy_audio(image_path: str, audio_path: str, output_path: str, audio_text: str):
    audio = AudioFileClip(audio_path)
    duration = audio.duration
    
    # Force audio to exact frame boundary
    fps = 24
    exact_duration = int(duration * fps) / fps
    audio = audio.subclip(0, exact_duration)
    duration = exact_duration

    clip = ImageClip(image_path, duration=duration)
    clip = clip.resize(newsize=(1920, 1080))

    if random.random() < 0.30:
        clip = clip.fadein(random.uniform(0.3, 1.0))
    if random.random() < 0.30:
        clip = clip.fadeout(random.uniform(0.3, 1.0))

    subtitles = split_text_by_time(audio_text, duration, max_chars=42)
    subtitle_clips = []

    for text, start, end in subtitles:
        img = create_caption_image(text, clip.w)
        txt = (
            ImageClip(img, transparent=True)
            .set_position(("center", 10))
            .set_start(start)
            .set_end(end)
        )
        subtitle_clips.append(txt)

    final = CompositeVideoClip([clip] + subtitle_clips, size=clip.size)
    final = final.set_audio(audio)
    final = final.set_duration(duration)

    final.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        audio_fps=44100,
        audio_nbytes=2,
        audio_buffersize=20000,  # Prevents audio glitches
        preset='medium',
        threads=4,
        logger=None
    )

    clip.close()
    audio.close()