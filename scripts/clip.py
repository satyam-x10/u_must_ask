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


def create_caption_image(text, width, fontsize=34, min_fontsize=34):
    # Render at 3x resolution for extreme crispness
    scale = 3

    final_height = 36   # EXACT SAME SIZE
    W = width * scale
    H = final_height * scale

    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Load crisp TrueType font only
    def load_ttf(size):
        for f in ["arial.ttf", "DejaVuSans.ttf"]:
            try:
                return ImageFont.truetype(f, size)
            except:
                pass
        raise RuntimeError("Missing TTF font — install arial or dejavu.")

    # Pick font
    fs = fontsize * scale
    font = load_ttf(fs)

    # Fit width
    while draw.textlength(text, font=font) > W - (12 * scale) and fs > min_fontsize * scale:
        fs -= scale
        font = load_ttf(fs)

    # CENTER Y USING FONT ASCENT/DESCENT = sharper text
    ascent, descent = font.getmetrics()
    text_h = ascent + descent
    y = (H - text_h) // 2

    # Much thinner stroke → stays sharp after downscale
    stroke = max(1, scale // 2)

    draw.text(
        ((W - draw.textlength(text, font=font)) / 2, y),
        text,
        font=font,
        fill=(255, 255, 255, 255),
        stroke_width=stroke*4,
        stroke_fill=(0, 0, 0, 255)
    )

    # PERFECTLY sharp downscale
    img = img.resize((width, final_height), Image.LANCZOS)

    return np.array(img)

def generate_scene_clip(image_path: str, audio_path: str, output_path: str, audio_text: str):
    audio = AudioFileClip(audio_path)
    duration = audio.duration

    clip = ImageClip(image_path, duration=duration)
    clip = clip.resize(newsize=(1920, 1080))    # FULL HD

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
        .set_end(end)

        subtitle_clips.append(txt)

    final = CompositeVideoClip([clip] + subtitle_clips, size=clip.size).set_audio(audio)

    final.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")

    clip.close()
    audio.close()
