import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from moviepy.editor import (
    VideoFileClip, ImageClip, CompositeVideoClip,
    AudioFileClip, ColorClip
)

W, H = 1920, 1080


# --------------------------
# TEXT RENDER FUNCTION
# --------------------------
def get_font(size, font_path=None):
    try:
        if font_path and os.path.exists(font_path):
            return ImageFont.truetype(font_path, size)
        return ImageFont.truetype("arial.ttf", size)
    except:
        return ImageFont.truetype("DejaVuSans.ttf", size)


def create_text_image_pil(text, font_size, color, max_width=1200, font_path=None):
    font = get_font(font_size, font_path)

    # Single line
    bbox = font.getbbox(text)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    img = Image.new("RGBA", (text_w + 20, text_h + 20), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.text((10, 10), text, font=font, fill=color)

    return img


# ------------------------------------------------------
# INTRO GENERATOR (Blur BG + Ring + Title Below Cat)
# ------------------------------------------------------
def generate_intro_clip(image_path: str, audio_path: str, title_text: str, duration: float = 2.5):
    print(f"Generating INTRO clip with image: {image_path}, audio: {audio_path}")

    pip_video = "static/vid/cat.mp4"

    # --------------------------------------------------
    # BLURRED BACKGROUND
    # --------------------------------------------------
    if os.path.exists(image_path):
        bg_img = Image.open(image_path).convert("RGB")
        bg_img = bg_img.resize((W, H), Image.LANCZOS)

        # Cinematic blur
        bg_img = bg_img.filter(ImageFilter.GaussianBlur(radius=25))

        base = ImageClip(np.array(bg_img)).set_duration(duration)
    else:
        base = ColorClip((W, H), color=(20, 20, 20)).set_duration(duration)

    # Subtle zoom-in
    base = base.resize(lambda t: 1.00 + 0.02 * t)
    layers = [base]

    # --------------------------------------------------
    # CAT VIDEO (CENTER CIRCLE + NEON RING)
    # --------------------------------------------------
    if os.path.exists(pip_video):
        cat = VideoFileClip(pip_video, audio=False)
        cat = cat.loop(duration=duration) if cat.duration < duration else cat.subclip(0, duration)

        # Square crop
        w, h = cat.size
        side = min(w, h)
        cat = cat.crop(
            x1=w/2 - side/2,
            y1=h/2 - side/2,
            width=side, height=side
        ).resize(height=450)

        # Circular mask
        def circle_mask(clip):
            Wc, Hc = clip.size
            Y, X = np.ogrid[:Hc, :Wc]
            dist = np.sqrt((X - Wc/2)**2 + (Y - Hc/2)**2)
            return (dist <= Wc/2).astype(float)

        cat = cat.add_mask()
        cat.mask.get_frame = lambda t: circle_mask(cat)
        cat_y = H//2 - 120
        cat = cat.set_position(("center", cat_y))
        layers.append(cat)

        # Neon ring
        ring_dia = 470
        ring_thickness = 9
        ring_img = Image.new("RGBA", (ring_dia, ring_dia), (0, 0, 0, 0))
        draw = ImageDraw.Draw(ring_img)
        draw.ellipse(
            (0, 0, ring_dia, ring_dia),
            outline=(0, 255, 255, 255),
            width=ring_thickness
        )

        # Glow layers
        blur1 = ring_img.filter(ImageFilter.GaussianBlur(6))
        blur2 = ring_img.filter(ImageFilter.GaussianBlur(14))

        final_ring = Image.alpha_composite(blur2, blur1)
        final_ring = Image.alpha_composite(final_ring, ring_img)

        ring_clip = ImageClip(np.array(final_ring)).set_duration(duration)
        ring_clip = ring_clip.set_position(("center", cat_y - (ring_dia - 450)//2))
        layers.append(ring_clip)

    # --------------------------------------------------
    # TITLE BELOW CAT (WITH BORDER)
    # --------------------------------------------------
    font_size = 60
    font = get_font(font_size)

    stroke_width = 3
    stroke_color = (0, 0, 0)  # black border

    # Render bordered title
    bbox = font.getbbox(title_text)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]

    title_img = Image.new("RGBA", (tw + 40, th + 40), (0, 0, 0, 0))
    draw = ImageDraw.Draw(title_img)

    draw.text(
        (20, 20),
        title_text,
        font=font,
        fill=(255, 255, 255),
        stroke_width=stroke_width,
        stroke_fill=stroke_color
    )

    title_clip = ImageClip(np.array(title_img), transparent=True) \
        .set_duration(duration) \
        .set_position(("center",160))

    layers.append(title_clip)

    # --------------------------------------------------
    # IMAGE PATH TEXT (BOTTOM LEFT)
    # --------------------------------------------------
    img_name = os.path.basename(image_path)
    path_img = create_text_image_pil(
        f"Source: {img_name}",
        font_size=34,
        color=(200, 200, 200)
    )

    path_clip = ImageClip(np.array(path_img), transparent=True) \
        .set_position((40, H - 80)) \
        .set_duration(duration)

    layers.append(path_clip)

    # --------------------------------------------------
    # FINAL COMPOSITE
    # --------------------------------------------------
    final = CompositeVideoClip(layers, size=(W, H))

    if os.path.exists(audio_path):
        audio = AudioFileClip(audio_path).volumex(1.0)
        final = final.set_audio(audio)

    return final
