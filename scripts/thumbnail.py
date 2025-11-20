from PIL import Image, ImageDraw
import random
import os

def create_clickbait_thumbnail(bg_path, cat_path, output_path):
    """
    Cat is always bottom aligned (10px above bottom)
    and can be anywhere horizontally (full random X range).
    """

    # Load images
    try:
        background = Image.open(bg_path).convert("RGBA")
        cat = Image.open(cat_path).convert("RGBA")
    except FileNotFoundError as e:
        print("Error:", e)
        return

    # Make cat very large (~90% height)
    target_cat_height = int(background.height * 0.90)
    aspect = cat.width / cat.height
    new_width = int(target_cat_height * aspect)
    cat = cat.resize((new_width, target_cat_height), Image.Resampling.LANCZOS)

    # Random rotation (-20 to +20)
    angle = random.randint(-20, 20)
    cat = cat.rotate(angle, expand=True, resample=Image.Resampling.BICUBIC)

    # X-position: fully random across whole width
    pos_x = random.randint(-250, 250)
    
    # Y-position: always bottom, with exactly 10px margin
    pos_y =  10

    # Composite
    final_img = background.copy()
    final_img.paste(cat, (pos_x, pos_y), cat)

    # Save
    final_img = final_img.convert("RGB")
    final_img.save(output_path, quality=95)
    print("Thumbnail saved:", output_path)

# --- Configuration ---
# Replace these with your actual file names
bg_image = "C:\\Users\\satyam\\Documents\\Youtube\\U must ask\\outputs\\thumbnails\\thumb_2.png"      # Your background
cat_image = "static\\img\\cat-exc.png"   # Your cat image (Ideally a transparent PNG)
output_file = "final_thumbnail.jpg"
comment_box_img= "static\\img\\comment_box.png"
title = "The Glitch in Reality We All Ignore"

if __name__ == "__main__":
    # Check if files exist before running
    if os.path.exists(bg_image) and os.path.exists(cat_image):
        # create_clickbait_thumbnail(bg_image, cat_image,  output_file)
        for i in range(13):
            output_file_variant = f"final_thumbnail_variant_{i+1}.jpg"
            create_clickbait_thumbnail(bg_image, cat_image, output_file_variant)
    else:
        print("Please ensure the background and cat image files exist at the specified paths.")