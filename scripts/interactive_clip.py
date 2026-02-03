
import os
import cv2
import numpy as np
from rembg import remove
from PIL import Image
from moviepy.editor import ImageClip, CompositeVideoClip, AudioFileClip, ColorClip, VideoClip
import random

def extract_layers(image_path):
    """
    Extracts foreground and background from an image.
    Returns:
        fg_pil (PIL.Image): RGBA foreground image.
        bg_pil (PIL.Image): RGB inpainted background image.
        original_pil (PIL.Image): Original image for review.
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
    
    return fg_pil, bg_pil, input_image

def verify_and_select_effect(fg_pil, original_pil):
    """
    Shows the cutout and asks for effect selection in the GUI.
    Returns: (bool valid, str choice)
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
    
    # ---------------------------------------------------------
    # OVERLAY ORIGINAL IMAGE PREVIEW
    # ---------------------------------------------------------
    try:
        # Resize original for thumbnail (max width 300px)
        orig_w, orig_h = original_pil.size
        thumb_scale = 300 / float(orig_w)
        thumb_h = int(orig_h * thumb_scale)
        thumb_w = 300
        
        thumb = original_pil.resize((thumb_w, thumb_h))
        thumb_np = np.array(thumb.convert("RGB"))
        thumb_bgr = cv2.cvtColor(thumb_np, cv2.COLOR_RGB2BGR)
        
        # Position: Top Left with padding
        pads = 20
        # Check if it fits
        if thumb_h + pads < h and thumb_w + pads < w:
            # Draw white border
            cv2.rectangle(checkerboard, (pads-2, pads-2), (pads+thumb_w+2, pads+thumb_h+2), (255, 255, 255), 2)
            # Paste thumbnail
            checkerboard[pads:pads+thumb_h, pads:pads+thumb_w] = thumb_bgr
            # Label
            cv2.putText(checkerboard, "Original", (pads, pads-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    except Exception as e:
        print(f"Preview error: {e}")
        pass
    # ---------------------------------------------------------

    # Overlay UI Text
    overlay = checkerboard.copy()
    cv2.rectangle(overlay, (0, h - 150), (w, h), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.7, checkerboard, 0.3, 0, checkerboard)

    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 0.6 if w < 1000 else 1.0
    thick = 1 if w < 1000 else 2
    color = (255, 255, 255)
    
    cv2.putText(checkerboard, "[1] Zoom Subject  [2] Parallax  [3] Floating  [4] Zoom BG", (20, h - 90), font, scale, color, thick)
    cv2.putText(checkerboard, "[S] Skip Scene/Effect", (20, h - 40), font, scale, (100, 100, 255), thick)
    
    cv2.imshow("Select Effect", checkerboard)
    
    while True:
        key = cv2.waitKey(0)
        
        # 's' or 'S' to skip
        if key == ord('s') or key == ord('S'):
            cv2.destroyAllWindows()
            return False, None
            
        # 1-4 to select
        if key == ord('1'): choice = "1"; break
        if key == ord('2'): choice = "2"; break
        if key == ord('3'): choice = "3"; break
        if key == ord('4'): choice = "4"; break

    cv2.destroyAllWindows()
    print(f"-> Selected Option: {choice}")
    return True, choice

def create_zooming_clip(pil_image_rgba, duration, max_zoom=1.05):
    """
    Creates a VideoClip that zooms the image using PIL to preserve Alpha channel correctness.
    Returns: VideoClip (RGBA)
    """
    w, h = pil_image_rgba.size
    
    def make_frame(t):
        progress = t / duration 
        # Calculate current scale
        scale = 1.0 + (max_zoom - 1.0) * progress
        
        new_w = int(w * scale)
        new_h = int(h * scale)
        
        # Resize using PIL
        resized = pil_image_rgba.resize((new_w, new_h), Image.Resampling.BILINEAR)
        return np.array(resized)

    # Create clip that returns RGBA
    clip = VideoClip(make_frame, duration=duration)
    
    # Separate Mask for MoviePy
    # We create a mask clip that extracts the alpha channel from the frame generator
    def make_mask(t):
        frame = make_frame(t)
        return frame[:, :, 3] / 255.0
        
    mask_clip = VideoClip(make_mask, duration=duration, ismask=True)
    
    # Create RGB clip
    def make_rgb(t):
        frame = make_frame(t)
        return frame[:, :, :3]
        
    rgb_clip = VideoClip(make_rgb, duration=duration)
    rgb_clip = rgb_clip.set_mask(mask_clip)
    
    return rgb_clip

def generate_interactive_clip(image_path, audio_path, output_path, audio_text=""):
    print(f"\nProcessing: {os.path.basename(image_path)}")
    
    # 1. Extract Layers
    fg_pil, bg_pil, original_pil = extract_layers(image_path)
    
    # 2. Verify and Select in one step (with preview)
    is_valid, choice = verify_and_select_effect(fg_pil, original_pil)
    
    if not is_valid:
        print("Skipping interactive effect for this scene. Using static image.")
        return False # Fallback to standard generation

    video_width = 1920
    video_height = 1080
        
    audio = AudioFileClip(audio_path)
    duration = audio.duration
    
    # Resize PIL images first to ensure consistency
    fg_pil = fg_pil.resize((video_width, video_height), Image.Resampling.LANCZOS)
    bg_pil = bg_pil.resize((video_width, video_height), Image.Resampling.LANCZOS)
    
    # Create Background Clip
    bg_clip = ImageClip(np.array(bg_pil), duration=duration)

    # For clips that DON'T need zoom, we can use simple ImageClip
    # But for consistency, let's instantiate basic ImageClips first
    # We will override them for specific effects
    
    fg_clip_static = ImageClip(np.array(fg_pil), transparent=True, duration=duration)
    
    final_clip = None

    if choice == "1": # Zoom Subject
        # Use custom function to handle resizing with transparency
        fg_clip = create_zooming_clip(fg_pil, duration, max_zoom=1.05)
        fg_clip = fg_clip.set_position(("center", "center"))
        
        # Slight zoom on BG too
        bg_clip = bg_clip.resize(lambda t: 1 + 0.05 * t / duration)
        bg_clip = bg_clip.set_position(("center", "center"))
        
        final_clip = CompositeVideoClip([bg_clip, fg_clip], size=(video_width, video_height))

    elif choice == "2": # Parallax (Move Position only, safe for ImageClip)
        # BG moves left
        bg_clip_large = bg_clip.resize(1.1)
        bg_clip_anim = bg_clip_large.set_position(lambda t: (-20 * t, "center"))
        
        # FG moves right
        fg_clip_anim = fg_clip_static.set_position(lambda t: (20 * t, "center"))
        
        final_clip = CompositeVideoClip([bg_clip_anim, fg_clip_anim], size=(video_width, video_height))
        
    elif choice == "3": # Floating (Move Position only, safe for ImageClip)
        # Gentle Bobbing
        fg_clip = fg_clip_static.set_position(lambda t: ("center", video_height/2 - fg_clip_static.h/2 + 10 * np.sin(2 * np.pi * t / 4)))
        final_clip = CompositeVideoClip([bg_clip, fg_clip], size=(video_width, video_height))
        
    elif choice == "4": # Zoom BG
        bg_clip = bg_clip.resize(lambda t: 1 + 0.1 * t / duration)
        fg_clip = fg_clip_static.set_position(("center", "center"))
        final_clip = CompositeVideoClip([bg_clip, fg_clip], size=(video_width, video_height))
        
    else:
        # Default
        final_clip = CompositeVideoClip([bg_clip, fg_clip_static], size=(video_width, video_height))

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
