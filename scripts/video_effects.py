# video_effects.py

import random
import numpy as np
from moviepy.editor import vfx
from PIL import Image

# --- Pillow compatibility patch ---
# MoviePy < 2.0 expects Image.ANTIALIAS, which was removed in Pillow >= 10.0
if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.Resampling.LANCZOS


def apply_zoom(clip, duration):
    """Custom smooth zoom-in effect (Ken Burns style)."""
    zoom_factor = random.uniform(1.05, 1.15)
    return clip.resize(lambda t: 1 + (zoom_factor - 1) * (t / duration))


def apply_pan(clip, duration):
    """Slow horizontal or vertical pan."""
    direction = random.choice(["horizontal", "vertical"])
    move_distance = random.randint(50, 150)

    if direction == "horizontal":
        return clip.set_position(lambda t: (-move_distance * t / duration, 0))
    else:
        return clip.set_position(lambda t: (0, -move_distance * t / duration))


def apply_rotate(clip, duration):
    """Gentle rotation for realism."""
    angle = random.uniform(-2, 2)
    return clip.rotate(angle, unit="deg", resample="bicubic")


def apply_fade(clip, duration):
    """Smooth fade-in/out transitions."""
    fade_time = min(0.8, duration / 4)
    return clip.fadein(fade_time).fadeout(fade_time)


def apply_blur_flicker(clip, duration):
    """Simulate light flicker with brightness and contrast changes."""
    def flicker(get_frame, t):
        frame = get_frame(t).astype(np.float32)
        lum_factor = 1 + random.uniform(-0.03, 0.03)
        frame *= lum_factor
        frame = np.clip(frame, 0, 255)
        return frame.astype(np.uint8)

    return clip.fl(flicker)


def get_random_effects():
    """Return a random combination of effects (2–3 per clip)."""
    all_effects = [
        # apply_zoom,
        apply_pan,
        # apply_rotate,
        # apply_fade,
        # apply_blur_flicker,
    ]
    return random.sample(all_effects, k=random.randint(2, 3))
