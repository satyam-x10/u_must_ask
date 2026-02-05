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
            .set_position(("center", 980))
            .set_start(start)
            .set_end(end)
        )
        subtitle_clips.append(txt)

    final = CompositeVideoClip([clip] + subtitle_clips, size=clip.size)
    
    # Write video only (Silent)
    final.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio=False,
        preset='medium',
        threads=4,
        logger=None
    )
    
    # Cleanup
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
    # final = final.set_audio(audio) # NO AUDIO
    final = final.set_duration(duration)

    final.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio=False, # NO AUDIO
        preset='medium',
        threads=4,
        logger=None
    )

    clip.close()
    audio.close()


def place_image_contain(canvas, img_path, box, bg_color=(0, 0, 0), border_color=None, border_width=0):
    """
    Helper: Resizes image to fit INSIDE 'box' (x, y, w, h) maintaining aspect ratio.
    Pastes it onto canvas. Centers it.
    """
    x, y, w, h = box
    try:
        img = Image.open(img_path).convert("RGBA")
    except Exception as e:
        print(f"Error opening {img_path}: {e}")
        return

    # Calculate aspect ratios
    target_ratio = w / h
    img_ratio = img.width / img.height

    if img_ratio > target_ratio:
        # Image is wider -> Fit to width
        new_w = w
        new_h = int(w / img_ratio)
    else:
        # Image is taller -> Fit to height
        new_h = h
        new_w = int(h * img_ratio)

    # Resize
    img = img.resize((new_w, new_h), Image.LANCZOS)

    # Add border if requested
    if border_color and border_width > 0:
        bordered = Image.new("RGBA", (new_w + 2*border_width, new_h + 2*border_width), border_color)
        bordered.paste(img, (border_width, border_width))
        img = bordered
        new_w += 2*border_width
        new_h += 2*border_width

    # Center position
    paste_x = x + (w - new_w) // 2
    paste_y = y + (h - new_h) // 2

    canvas.paste(img, (paste_x, paste_y), mask=img)

# --- 2 IMAGE TEMPLATES ---

def t2_vertical_split(paths, W, H):
    # Split L/R
    canvas = Image.new("RGB", (W, H), (20, 20, 20))
    place_image_contain(canvas, paths[0], (0, 0, W//2, H))
    place_image_contain(canvas, paths[1], (W//2, 0, W//2, H))
    # Divider
    draw = ImageDraw.Draw(canvas)
    draw.line([(W//2, 0), (W//2, H)], fill="white", width=4)
    return canvas

def t2_horizontal_split(paths, W, H):
    # Split Top/Bottom
    canvas = Image.new("RGB", (W, H), (20, 20, 20))
    place_image_contain(canvas, paths[0], (0, 0, W, H//2))
    place_image_contain(canvas, paths[1], (0, H//2, W, H//2))
    draw = ImageDraw.Draw(canvas)
    draw.line([(0, H//2), (W, H//2)], fill="white", width=4)
    return canvas

def t2_diagonal_pip(paths, W, H):
    # Background blurred, images as cards
    canvas = Image.new("RGB", (W, H), (30, 30, 30))
    # Top Left Large
    place_image_contain(canvas, paths[0], (50, 50, int(W*0.6), int(H*0.6)), border_color="white", border_width=10)
    # Bottom Right Large
    place_image_contain(canvas, paths[1], (int(W*0.35), int(H*0.35), int(W*0.6), int(H*0.6)), border_color="white", border_width=10)
    return canvas

def t2_polaroid_side(paths, W, H):
    canvas = Image.new("RGB", (W, H), (10, 10, 15))
    margin = 50
    w_box = (W - 3*margin) // 2
    h_box = H - 2*margin
    place_image_contain(canvas, paths[0], (margin, margin, w_box, h_box), border_color="white", border_width=15)
    place_image_contain(canvas, paths[1], (2*margin + w_box, margin, w_box, h_box), border_color="white", border_width=15)
    return canvas

def t2_floating_overlap(paths, W, H):
    canvas = Image.new("RGB", (W, H), (50, 50, 50))
    # Img 1 center
    place_image_contain(canvas, paths[0], (0, 0, int(W*0.55), H), border_color="white", border_width=5)
    place_image_contain(canvas, paths[1], (int(W*0.45), int(H*0.2), int(W*0.55), int(H*0.6)), border_color="white", border_width=5)
    return canvas

# --- 3 IMAGE TEMPLATES ---

def t3_columns(paths, W, H):
    canvas = Image.new("RGB", (W, H), (10, 10, 10))
    cw = W // 3
    for i in range(3):
        place_image_contain(canvas, paths[i], (i*cw, 0, cw, H))
        if i > 0:
            draw = ImageDraw.Draw(canvas)
            draw.line([(i*cw, 0), (i*cw, H)], fill="white", width=4)
    return canvas

def t3_one_left_two_right(paths, W, H):
    canvas = Image.new("RGB", (W, H), (10, 10, 10))
    # Left Half
    place_image_contain(canvas, paths[0], (0, 0, W//2, H))
    # Right Top
    place_image_contain(canvas, paths[1], (W//2, 0, W//2, H//2))
    # Right Bottom
    place_image_contain(canvas, paths[2], (W//2, H//2, W//2, H//2))
    
    draw = ImageDraw.Draw(canvas)
    draw.line([(W//2, 0), (W//2, H)], fill="white", width=4)
    draw.line([(W//2, H//2), (W, H//2)], fill="white", width=4)
    return canvas

def t3_one_top_two_bottom(paths, W, H):
    canvas = Image.new("RGB", (W, H), (10, 10, 10))
    # Top Half
    place_image_contain(canvas, paths[0], (0, 0, W, H//2))
    # Bot Left
    place_image_contain(canvas, paths[1], (0, H//2, W//2, H//2))
    # Bot Right
    place_image_contain(canvas, paths[2], (W//2, H//2, W//2, H//2))
    
    draw = ImageDraw.Draw(canvas)
    draw.line([(0, H//2), (W, H//2)], fill="white", width=4)
    draw.line([(W//2, H//2), (W//2, H)], fill="white", width=4)
    return canvas

def t3_grid_cards(paths, W, H):
    # 3 images floating
    canvas = Image.new("RGB", (W, H), (40, 40, 45))
    # 1 Top Left
    place_image_contain(canvas, paths[0], (50, 50, int(W*0.45), int(H*0.45)), border_color="white", border_width=8)
    # 2 Top Right
    place_image_contain(canvas, paths[1], (int(W*0.5)+20, 50, int(W*0.45), int(H*0.45)), border_color="white", border_width=8)
    # 3 Bottom Center
    place_image_contain(canvas, paths[2], (int(W*0.25), int(H*0.5)+20, int(W*0.5), int(H*0.45)), border_color="white", border_width=8)
    return canvas

def t3_steps(paths, W, H):
    # Diagonal steps
    canvas = Image.new("RGB", (W, H), (20, 20, 25))
    # 1 Left
    place_image_contain(canvas, paths[0], (20, 20, int(W*0.3), int(H*0.6)), border_color="white", border_width=5)
    # 2 Center
    place_image_contain(canvas, paths[1], (int(W*0.35), int(H*0.2), int(W*0.3), int(H*0.6)), border_color="white", border_width=5)
    # 3 Right
    place_image_contain(canvas, paths[2], (int(W*0.68), int(H*0.38), int(W*0.3), int(H*0.6)), border_color="white", border_width=5)
    return canvas


def create_collage(image_paths, output_path, width=1920, height=1080):
    """
    Combines multiple images into a single collage using random templates.
    Ensures NO cropping (images are fitted/contained).
    """
    if not image_paths:
        return None

    count = len(image_paths)
    canvas = None
    
    # Randomly select a template
    if count == 2:
        templates = [t2_vertical_split, t2_horizontal_split, t2_diagonal_pip, t2_polaroid_side, t2_floating_overlap]
        tmpl = random.choice(templates)
        print(f"  -> Using 2-Image Template: {tmpl.__name__}")
        canvas = tmpl(image_paths, width, height)
        
    elif count >= 3:
        # If more than 3, just take first 3 for now or stick to 3 logic
        # User said "2 or 3 images .. no more"
        use_paths = image_paths[:3]
        templates = [t3_columns, t3_one_left_two_right, t3_one_top_two_bottom, t3_grid_cards, t3_steps]
        tmpl = random.choice(templates)
        print(f"  -> Using 3-Image Template: {tmpl.__name__}")
        canvas = tmpl(use_paths, width, height)
    
    else:
        # Single image? Just copy it I guess, or center it
        canvas = Image.new("RGB", (width, height), (0,0,0))
        place_image_contain(canvas, image_paths[0], (0, 0, width, height))

    if canvas:
        canvas.save(output_path)
        return output_path
    return None