import random
import textwrap
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


def create_caption_image(text, width, fontsize=16, min_fontsize=16):
    W = width
    H = 20  # smaller height since single-line

    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Load font
    try:
        font = ImageFont.truetype("arial.ttf", fontsize)
    except:
        font = ImageFont.load_default()

    # Reduce font size until text fits
    while draw.textlength(text, font=font) > W and fontsize > min_fontsize:
        fontsize -= 2
        try:
            font = ImageFont.truetype("arial.ttf", fontsize)
        except:
            font = ImageFont.load_default()

    # Draw final single-line text
    w = draw.textlength(text, font=font)
    draw.text(
        ((W - w) / 2, (H - fontsize) / 2),
        text,
        font=font,
        fill="white",
        stroke_width=2,
        stroke_fill="black"
    )

    return np.array(img)

def generate_scene_clip(image_path: str, audio_path: str, output_path: str, audio_text: str):
    audio = AudioFileClip(audio_path)
    duration = audio.duration

    clip = ImageClip(image_path, duration=duration)

    if random.random() < 0.30:
        clip = clip.fadein(random.uniform(0.3, 1.0))
    if random.random() < 0.30:
        clip = clip.fadeout(random.uniform(0.3, 1.0))

    subtitles = split_text_by_time(audio_text, duration, max_chars=42)
    subtitle_clips = []

    for text, start, end in subtitles:
        img = create_caption_image(text, clip.w)
        txt = ImageClip(img, transparent=True) \
                .set_position(("center", 10)) \
                .set_start(start) \
                .set_end(end) \
                .fadein(0.15) \
                .fadeout(0.15)
        subtitle_clips.append(txt)

    final = CompositeVideoClip([clip] + subtitle_clips, size=clip.size).set_audio(audio)

    final.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")

    clip.close()
    audio.close()
