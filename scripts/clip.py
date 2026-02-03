import random
import textwrap
import subprocess
import os
import math
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip
import cv2

# Import effects library
import scripts.video_effects as effects

def create_caption_image(text, width, fontsize=55, min_fontsize=40):
    """
    Creates a high-quality caption image with stroke.
    """
    # Render at 3x resolution for extreme sharpness
    scale = 3
    final_height = 80  # Increased height for bigger text
    W = width * scale
    H = final_height * scale

    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    def load_ttf(size):
        # Try common fonts
        options = ["arialbd.ttf", "arial.ttf", "seguiemj.ttf", "DejaVuSans-Bold.ttf", "DejaVuSans.ttf"]
        for f in options:
            try:
                return ImageFont.truetype(f, size)
            except:
                pass
        # Fallback to default if no TTF found (unlikely on Windows)
        return ImageFont.load_default()

    fs = fontsize * scale
    font = load_ttf(fs)

    # Shrink font if wider than allowed
    margin = 50 * scale
    while draw.textlength(text, font=font) > W - margin and fs > min_fontsize * scale:
        fs -= scale
        font = load_ttf(fs)

    ascent, descent = font.getmetrics()
    text_h = ascent + descent
    y = (H - text_h) // 2

    stroke_width = max(3, scale // 1)
    
    # Shadow / Stroke
    draw.text(
        ((W - draw.textlength(text, font=font)) / 2, y),
        text,
        font=font,
        fill="white",
        stroke_width=stroke_width * 5,
        stroke_fill="black"
    )

    img = img.resize((width, final_height), Image.LANCZOS)
    return np.array(img)

def apply_random_effect(clip, image_path, duration):
    """
    Applies a random motion effect from the effects library.
    """
    # List of available effect functions in video_effects.py
    effect_options = [
        effects.pan_left_right,
        effects.pan_right_left,
        effects.pan_up_down,
        effects.pan_down_up,
        effects.zoom_in_center,
        effects.zoom_in_top,
        effects.zoom_in_bottom,
        effects.slight_rotation,
        effects.subtle_tilt,
        effects.parallax_shift,
        # effects.brightness_pulse, # Can be distracting
        # effects.contrast_wave,    # Can be distracting
        effects.warm_light_glow,
        effects.vignette_fade,
        effects.subtle_color_shift
    ]
    
    selected_effect = random.choice(effect_options)
    print(f"Applying effect: {selected_effect.__name__}")

    # Read original image again with OpenCV for the effect
    # (MoviePy's 'fl' receives a frame, but our effects assume they process frames)
    # The 'fl' function in MoviePy passes a 'get_frame' function and time 't'
    
    def effect_generator(get_frame, t):
        frame = get_frame(t) # RGB numpy array
        
        # Determine strict output size (1080p usually)
        h, w = frame.shape[:2]
        
        # Apply the OpenCV effect
        # Note: most effects in video_effects.py assume RGB/BGR numpy arrays
        # MoviePy uses RGB. OpenCV uses BGR by default if reading from file, 
        # but here 'frame' is from MoviePy so it's RGB. 
        # CAVEAT: Some cv2 functions expect BGR for certain color conversions, 
        # but for geometric transforms (Pan/Zoom) color space doesn't matter.
        
        processed = selected_effect(frame, t, duration)
        
        # Ensure consistent output size (resize back if effect cropped it)
        if processed.shape[0] != h or processed.shape[1] != w:
            processed = cv2.resize(processed, (w, h), interpolation=cv2.INTER_LINEAR)
            
        return processed

    return clip.fl(effect_generator)


def split_text_smart(text, max_chars=40):
    """
    Splits text into chunks that make sense, not just by char usage.
    """
    import textwrap
    return textwrap.wrap(text, width=max_chars, break_long_words=False)

def split_text_by_time(text: str, audio_duration: float, max_chars=40):
    words = split_text_smart(text, max_chars)
    if not words:
        return []
    
    count = len(words)
    segment_duration = audio_duration / count
    
    result = []
    current_time = 0.0
    
    for line in words:
        end_time = current_time + segment_duration
        result.append((line, current_time, end_time))
        current_time = end_time
        
    return result

def generate_scene_clip(image_path: str, audio_path: str, output_path: str, audio_text: str):
    
    # Load Audio
    try:
        audio = AudioFileClip(audio_path)
    except Exception as e:
        print(f"Error loading audio {audio_path}: {e}")
        return

    duration = audio.duration
    
    # 1. Base Image Clip
    clip = ImageClip(image_path, duration=duration)
    clip = clip.resize(newsize=(1920, 1080)) # Ensure standard HD

    # 2. Apply Dynamic Motion Effect (ALWAYS)
    try:
        clip = apply_random_effect(clip, image_path, duration)
    except Exception as e:
        print(f"Effect failed: {e}. using static image.")
    
    # 3. Fade In/Out Logic
    lower_name = os.path.basename(image_path).lower()
    if "intro" in lower_name:
        clip = clip.fadein(0.5).fadeout(0.5)
    elif "outro" in lower_name:
        clip = clip.fadeout(1.0)
    else:
        # Random transitions for middle clips
        if random.random() < 0.2:
            clip = clip.fadein(0.5)
        if random.random() < 0.2:
            clip = clip.fadeout(0.5)

    # 4. Generate Subtitles
    try:
        subtitles = split_text_by_time(audio_text, duration, max_chars=50) # Increased char limit
        subtitle_clips = []

        for text, start, end in subtitles:
            # Create caption image
            img_array = create_caption_image(text, clip.w) # Width of the video
            
            # Create ImageClip for the text
            # Fix: Avoid .margin() as it caused crashes on some scenes. 
            # Manually position 80px from bottom.
            # Clip height is 1080. Subtitle image height is 80 (final_height)
            # Y position = 1080 - 80 - 80 = 920
            txt_clip = (ImageClip(img_array)
                        .set_start(start)
                        .set_end(end)
                        .set_position(("center", 920)) 
                       )
            subtitle_clips.append(txt_clip)
    except Exception as e:
        print(f"Subtitle generation failed for scene: {e}")
        subtitle_clips = []

    # 5. Composite Syle
    final = CompositeVideoClip([clip] + subtitle_clips, size=clip.size)
    
    # 6. Export with robust FFmpeg muxing
    temp_video = output_path.replace(".mp4", "_temp.mp4")
    
    # Write video stream only (fast)
    final.write_videofile(
        temp_video,
        fps=30,             # Smoother 30fps
        codec="libx264",
        audio=False,
        preset="fast",      # Balanced speed/quality
        threads=4,
        logger=None
    )

    # Mux with original audio
    subprocess.run([
        "ffmpeg", "-y",
        "-i", temp_video,
        "-i", audio_path,
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",     # High quality audio
        "-shortest",
        "-avoid_negative_ts", "make_zero",
        output_path
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Cleanup
    if os.path.exists(temp_video):
        os.remove(temp_video)
    
    clip.close()
    audio.close()
    final.close()
