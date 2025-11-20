from PIL import Image, ImageDraw, ImageFont
import textwrap
import random
import os


def crop_to_visible(img):
    """Auto-crop the black background around the speech bubble."""
    # Convert to RGB + get bounding box of non-black areas
    bbox = img.convert("RGB").point(lambda p: 255 if p > 10 else 0).getbbox()
    if bbox:
        return img.crop(bbox)
    return img


def create_clickbait_thumbnail(bg_path, cat_path, box_path, title, output_path):
    """
    FINAL VERSION:
    - Comment box centered at top (10px gap), ±20px wiggle
    - Box auto-cropped to remove black background (tail preserved)
    - Text centered inside box
    - Cat bottom aligned (10px gap)
    """

    # Load images
    try:
        background = Image.open(bg_path).convert("RGBA")
        cat = Image.open(cat_path).convert("RGBA")
        box_raw = Image.open(box_path).convert("RGBA")
    except FileNotFoundError as e:
        print("Error:", e)
        return

    # --- AUTO-CROP SPEECH BUBBLE (keep tail, remove black background) ---
    box = crop_to_visible(box_raw)

    # --- Resize cat ---
    target_cat_height = int(background.height * 0.90)
    aspect = cat.width / cat.height
    new_width = int(target_cat_height * aspect)
    cat = cat.resize((new_width, target_cat_height), Image.Resampling.LANCZOS)

    # Small rotation
    angle = random.randint(-20, 20)
    cat = cat.rotate(angle, expand=True, resample=Image.Resampling.BICUBIC)

    # Random X position
    pos_x = random.randint(-250, 250)

    # Bottom align cat
    pos_y = 10

    # Paste cat
    final_img = background.copy()
    final_img.paste(cat, (pos_x, pos_y), cat)

    # ---------------------------
    # COMMENT BOX 70% SIZE
    # ---------------------------

    max_box_width = int(background.width * 0.95)
    base_width = int(background.width * 0.45)

    # Previous = base_width * 3
    # New = 70% of that
    box_width = int(min(max_box_width, int(base_width * 3)) * 0.60)

    box_aspect = box.width / box.height
    box_height = int(box_width / box_aspect)

    box_resized = box.resize((box_width, box_height), Image.Resampling.LANCZOS)

    padding = 28   # reduced with size scaling
    text_area_w = box_width - 2 * padding
    text_area_h = box_height - 2 * padding

    draw = ImageDraw.Draw(final_img)

    # 70% font scaling
    try:
        font_path = "arial.ttf"
        font_size = int(35 * 0.70)  # ≈ 24
        font = ImageFont.truetype(font_path, font_size)
    except:
        font = ImageFont.load_default()

    # Fit text to smaller bubble
    wrapped = None
    while font_size > 12:
        try:
            font = ImageFont.truetype(font_path, font_size)
        except:
            font = ImageFont.load_default()

        wrapped = textwrap.wrap(title, width=30)
        w, h = draw.multiline_textbbox((0, 0), "\n".join(wrapped), font=font)[2:]

        if w <= text_area_w and h <= text_area_h:
            break

        font_size -= 1

    if len(wrapped) > 5:
        wrapped = wrapped[:5]
        wrapped[-1] += "..."

    final_text = "\n".join(wrapped)


    # ---------------------------
    # POSITION BOX TOP-CENTER
    # ---------------------------

    horizontal_wiggle = random.randint(-20, 20)

    box_x = (background.width - box_width) // 2 + horizontal_wiggle
    box_y = 10  # 10px from top

    box_x = max(0, min(background.width - box_width, box_x))

    final_img.paste(box_resized, (box_x, box_y), box_resized)

    # ---------------------------
    # CENTER TEXT INSIDE BUBBLE
    # ---------------------------
    text_w, text_h = draw.multiline_textbbox((0, 0), final_text, font=font)[2:]

    text_x = box_x + (box_width - text_w) // 2
    text_y = box_y + (box_height - text_h) // 2 - 16  # CENTERED

    draw.multiline_text(
        (text_x, text_y),
        final_text,
        font=font,
        fill="black",
        align="center"
    )

    # Save final thumbnail
    final_img = final_img.convert("RGB")
    final_img.save(output_path, quality=95)
    print("Thumbnail saved:", output_path)
