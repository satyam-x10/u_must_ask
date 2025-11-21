import random
import textwrap
import subprocess
import os
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip
import cv2
from moviepy.video.fx.all import crop as mpy_crop

def get_subject_bbox(image_path, expand_factor=1.3, min_area_fraction=0.002):
    """
    Return (x, y, w, h) of the most salient region in the image.
    If detection fails, return None.
    """
    img = cv2.imread(image_path)
    if img is None:
        return None
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    try:
        saliency = cv2.saliency.StaticSaliencySpectralResidual_create()
        (success, salmap) = saliency.computeSaliency(img)
        if not success or salmap is None:
            return None
        salmap = (salmap * 255).astype("uint8")
        _, thresh = cv2.threshold(salmap, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return None

        # Find largest contour by area
        areas = [(cv2.contourArea(c), c) for c in contours]
        areas.sort(key=lambda x: x[0], reverse=True)
        largest_area, largest_cnt = areas[0]
        h_img, w_img = gray.shape

        # Ignore contours that are extremely small
        if largest_area < min_area_fraction * (w_img * h_img):
            return None

        x, y, w, h = cv2.boundingRect(largest_cnt)

        # Expand bbox a bit
        cx = x + w / 2.0
        cy = y + h / 2.0
        w_exp = min(w_img, w * expand_factor)
        h_exp = min(h_img, h * expand_factor)
        x_exp = max(0, int(cx - w_exp / 2.0))
        y_exp = max(0, int(cy - h_exp / 2.0))
        w_exp = int(min(w_img - x_exp, w_exp))
        h_exp = int(min(h_img - y_exp, h_exp))

        return (x_exp, y_exp, w_exp, h_exp)
    except Exception:
        # Saliency may not be available on some OpenCV builds; fail gracefully.
        return None

def apply_ken_burns(clip, image_path, duration):
    """
    Works with ALL MoviePy versions.
    Smooth zoom-in or zoom-out using a function that modifies frame pixels.
    """

    # Detect subject bounding box
    bbox = get_subject_bbox(image_path)
    w_img, h_img = clip.size

    if bbox is None:
        # Fallback centered subject box
        short = min(w_img, h_img)
        box_w = int(short * 0.40)
        box_h = int(short * 0.40)
        x = int((w_img - box_w) / 2)
        y = int((h_img - box_h) / 2)
        bbox = (x, y, box_w, box_h)

    x_s, y_s, w_s, h_s = bbox

    # Choose zoom type
    zoom_in = random.random() < 0.5

    # Define start & end rectangles
    if zoom_in:
        start_rect = (0, 0, w_img, h_img)
        end_rect = (x_s, y_s, x_s + w_s, y_s + h_s)
    else:
        start_rect = (x_s, y_s, x_s + w_s, y_s + h_s)
        end_rect = (0, 0, w_img, h_img)

    # Smooth interpolation
    def lerp(a, b, t):
        return a + (b - a) * t

    # Frame processor
    def kb_frame(get_frame, t):
        frame = get_frame(t)

        # fraction of progress 0→1
        f = min(max(t / duration, 0), 1)

        x1 = int(lerp(start_rect[0], end_rect[0], f))
        y1 = int(lerp(start_rect[1], end_rect[1], f))
        x2 = int(lerp(start_rect[2], end_rect[2], f))
        y2 = int(lerp(start_rect[3], end_rect[3], f))

        # crop
        cropped = frame[y1:y2, x1:x2]

        # resize back to original
        cropped = cv2.resize(cropped, (w_img, h_img), interpolation=cv2.INTER_LINEAR)

        return cropped

    # Apply Ken Burns effect
    return clip.fl(kb_frame, apply_to=['mask'])


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

    final_height = 36  # FIXED caption height
    W = width * scale
    H = final_height * scale

    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    def load_ttf(size):
        for f in ["arial.ttf", "DejaVuSans.ttf"]:
            try:
                return ImageFont.truetype(f, size)
            except:
                pass
        raise RuntimeError("Missing TTF font — install arial or dejavu.")

    fs = fontsize * scale
    font = load_ttf(fs)

    # Shrink font if wider than allowed
    while draw.textlength(text, font=font) > W - (12 * scale) and fs > min_fontsize * scale:
        fs -= scale
        font = load_ttf(fs)

    ascent, descent = font.getmetrics()
    text_h = ascent + descent
    y = (H - text_h) // 2

    stroke = max(1, scale // 2)

    draw.text(
        ((W - draw.textlength(text, font=font)) / 2, y),
        text,
        font=font,
        fill=(255, 255, 255, 255),
        stroke_width=stroke * 4,
        stroke_fill=(0, 0, 0, 255),
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

    if random.random() < (1.0/3.0):
        try:
            clip = apply_ken_burns(clip, image_path, duration)
        except Exception as e:
            # Fail gracefully: keep original clip if something goes wrong
            print("KenBurns failed:", e)
    lower_name = os.path.basename(image_path).lower()

    # Fade logic based on filename
    lower_name = os.path.basename(image_path).lower()

    if "intro" in lower_name:
        clip = clip.fadein(0.8).fadeout(0.8)

    elif "outro" in lower_name:
        clip = clip.fadeout(0.8)

    else:
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