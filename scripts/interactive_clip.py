
import os
import cv2
import numpy as np
from rembg import remove
from PIL import Image
from moviepy.editor import ImageClip, CompositeVideoClip, AudioFileClip, ColorClip
import random

def extract_layers(image_path):
    """
    Extracts foreground and background from an image.
    Returns:
        fg_pil (PIL.Image): RGBA foreground image.
        bg_pil (PIL.Image): RGB inpainted background image.
    """
    input_image = Image.open(image_path)
    
    # 1. Remove background using rembg
    fg_pil = remove(input_image)
    
    # 2. Create Mask for Inpainting
    fg_np = np.array(fg_pil)
    alpha = fg_np[:, :, 3]
    # Dilate mask slightly to ensure clean edges for inpainting
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.dilate(alpha, kernel, iterations=2)
    
    # 3. Inpaint Background using OpenCV
    img_np = np.array(input_image.convert("RGB"))
    # cv2.inpaint requires BGR image and single channel mask
    img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    
    # Radius 3, NS method
    inpainted_bgr = cv2.inpaint(img_bgr, mask, 3, cv2.INPAINT_TELEA)
    inpainted_rgb = cv2.cvtColor(inpainted_bgr, cv2.COLOR_BGR2RGB)
    
    bg_pil = Image.fromarray(inpainted_rgb)
    
    return fg_pil, bg_pil

def verify_cutout(fg_pil):
    """
    Shows the cutout to the user for verification.
    """
    # Convert to BGR for OpenCV
    fg_np = np.array(fg_pil)
    bgr_image = cv2.cvtColor(fg_np, cv2.COLOR_RGBA2BGRA)
    
    # Create a checkerboard background
    h, w, _ = bgr_image.shape
    checkerboard = np.zeros((h, w, 3), dtype=np.uint8)
    tile_size = 20
    for y in range(0, h, tile_size):
        for x in range(0, w, tile_size):
            if (x // tile_size + y // tile_size) % 2 == 0:
                checkerboard[y:y+tile_size, x:x+tile_size] = (200, 200, 200)
            else:
                checkerboard[y:y+tile_size, x:x+tile_size] = (100, 100, 100)

    # Composite FG over Checkerboard
    alpha = bgr_image[:, :, 3] / 255.0
    for c in range(3):
        checkerboard[:, :, c] = (1.0 - alpha) * checkerboard[:, :, c] + alpha * bgr_image[:, :, c]
    
    cv2.imshow("Verify Cutout (Press 'y' to accept, 's' to skip)", checkerboard)
    key = cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    if key == ord('y') or key == ord('Y'):
        return True
    return False

def apply_zoom_effect(clip, zoom_ratio=0.04):
    """ Applies a gentle zoom effect """
    return clip.resize(lambda t: 1 + zoom_ratio * t / clip.duration)

def apply_pan_effect(clip, direction="left", speed=20):
    """ Applies a pan effect """
    w, h = clip.size
    if direction == "left":
        return clip.set_position(lambda t: (-speed * t, "center"))
    elif direction == "right":
        # Start from left edge (negative) to center? No, easier to just move
        return clip.set_position(lambda t: (speed * t - 50, "center")) # Simple implementation
    return clip

def generate_interactive_clip(image_path, audio_path, output_path, audio_text=""):
    print(f"\nProcessing: {os.path.basename(image_path)}")
    
    # 1. Extract Layers
    fg_pil, bg_pil = extract_layers(image_path)
    
    # 2. Verify
    if not verify_cutout(fg_pil):
        print("Skipping interactive effect for this scene. Using static image.")
        return False # Fallback to standard generation

    # 3. Select Effect
    print("\nSelect Effect:")
    print("1. Zoom Subject (Background Static)")
    print("2. Parallax (Subject moves Right, BG moves Left)")
    print("3. Floating (Gentle movement)")
    print("4. Just Zoom Background")
    
    try:
        choice = input("Enter choice (1-4): ").strip()
    except:
        choice = "1"
        
    audio = AudioFileClip(audio_path)
    duration = audio.duration
    
    # Create Clips
    # Resize to standard 1080p just in case
    fg_pil = fg_pil.resize((1920, 1080), Image.Resampling.LANCZOS)
    bg_pil = bg_pil.resize((1920, 1080), Image.Resampling.LANCZOS)
    
    bg_clip = ImageClip(np.array(bg_pil), duration=duration)
    fg_clip = ImageClip(np.array(fg_pil), transparent=True, duration=duration)
    
    final_clip = None

    if choice == "1": # Zoom Subject
        # Scale FG up
        fg_clip = fg_clip.resize(lambda t: 1 + 0.1 * t / duration) 
        # Center FG 
        fg_clip = fg_clip.set_position(("center", "center"))
        final_clip = CompositeVideoClip([bg_clip, fg_clip], size=(1920, 1080))

    elif choice == "2": # Parallax
        # BG moves left
        # We need BG to be slightly larger to pan
        bg_clip_large = bg_clip.resize(1.1)
        bg_clip_anim = bg_clip_large.set_position(lambda t: (-20 * t, "center"))
        
        # FG moves right
        fg_clip_anim = fg_clip.set_position(lambda t: (20 * t, "center"))
        
        final_clip = CompositeVideoClip([bg_clip_anim, fg_clip_anim], size=(1920, 1080))
        
    elif choice == "3": # Floating
        # Gentle Bobbing
        fg_clip = fg_clip.set_position(lambda t: ("center", 540 - fg_clip.h/2 + 10 * np.sin(2 * np.pi * t / 2)))
        final_clip = CompositeVideoClip([bg_clip, fg_clip], size=(1920, 1080))
        
    elif choice == "4": # Zoom BG
        bg_clip = bg_clip.resize(lambda t: 1 + 0.1 * t / duration)
        fg_clip = fg_clip.set_position(("center", "center"))
        final_clip = CompositeVideoClip([bg_clip, fg_clip], size=(1920, 1080))
        
    else:
        # Default Zoom Subject
        fg_clip = fg_clip.resize(lambda t: 1 + 0.1 * t / duration)
        fg_clip = fg_clip.set_position(("center", "center"))
        final_clip = CompositeVideoClip([bg_clip, fg_clip], size=(1920, 1080))

    # Add Audio
    final_clip = final_clip.set_audio(audio)
    
    # Write File
    final_clip.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        logger=None
    )
    
    return True
