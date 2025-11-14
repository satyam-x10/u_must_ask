import numpy as np
import cv2
import math

# Smooth easing
def ease_in_out(t, duration):
    x = t / duration
    return x * x * (3 - 2 * x)

##############################################
# 1. PAN LEFT → RIGHT
##############################################
def pan_left_right(frame, t, duration):
    h, w = frame.shape[:2]
    p = ease_in_out(t, duration)
    shift = int(p * (w * 0.10))
    return frame[:, shift:w]


##############################################
# 2. PAN RIGHT → LEFT
##############################################
def pan_right_left(frame, t, duration):
    h, w = frame.shape[:2]
    p = ease_in_out(t, duration)
    shift = int(p * (w * 0.10))
    return frame[:, 0:w-shift]


##############################################
# 3. PAN UP → DOWN
##############################################
def pan_up_down(frame, t, duration):
    h, w = frame.shape[:2]
    p = ease_in_out(t, duration)
    shift = int(p * (h * 0.10))
    return frame[shift:h, :]


##############################################
# 4. PAN DOWN → UP
##############################################
def pan_down_up(frame, t, duration):
    h, w = frame.shape[:2]
    p = ease_in_out(t, duration)
    shift = int(p * (h * 0.10))
    return frame[0:h-shift, :]


##############################################
# 5. ZOOM IN (Centered)
##############################################
def zoom_in_center(frame, t, duration):
    h, w = frame.shape[:2]
    p = ease_in_out(t, duration)

    zoom = 1 + p * 0.07  # 7% zoom stable
    crop_w = int(w / zoom)
    crop_h = int(h / zoom)

    x1 = (w - crop_w) // 2
    y1 = (h - crop_h) // 2

    return frame[y1:y1+crop_h, x1:x1+crop_w]


##############################################
# 6. ZOOM IN TOP
##############################################
def zoom_in_top(frame, t, duration):
    h, w = frame.shape[:2]
    p = ease_in_out(t, duration)

    zoom = 1 + p * 0.07
    crop_w = int(w / zoom)
    crop_h = int(h / zoom)

    x1 = (w - crop_w) // 2
    y1 = 0

    return frame[y1:y1+crop_h, x1:x1+crop_w]


##############################################
# 7. ZOOM IN BOTTOM
##############################################
def zoom_in_bottom(frame, t, duration):
    h, w = frame.shape[:2]
    p = ease_in_out(t, duration)

    zoom = 1 + p * 0.07
    crop_w = int(w / zoom)
    crop_h = int(h / zoom)

    x1 = (w - crop_w) // 2
    y1 = h - crop_h

    return frame[y1:h, x1:x1+crop_w]


##############################################
# 8. Slight Rotation
##############################################
def slight_rotation(frame, t, duration):
    angle = ease_in_out(t, duration) * 2  # max 2 degrees
    h, w = frame.shape[:2]

    m = cv2.getRotationMatrix2D((w//2, h//2), angle, 1)
    return cv2.warpAffine(frame, m, (w, h), borderMode=cv2.BORDER_REPLICATE)


##############################################
# 9. Tilt (horizontal)
##############################################
def subtle_tilt(frame, t, duration):
    h, w = frame.shape[:2]
    shift = int(math.sin((t/duration) * math.pi) * 5)
    m = np.float32([[1, 0, shift], [0, 1, 0]])
    return cv2.warpAffine(frame, m, (w, h), borderMode=cv2.BORDER_REPLICATE)


##############################################
# 10. Parallax Shift
##############################################
def parallax_shift(frame, t, duration):
    h, w = frame.shape[:2]
    shift = int(ease_in_out(t, duration) * 12)
    return frame[:, shift:w]


##############################################
# 11. Brightness Pulse
##############################################
def brightness_pulse(frame, t, duration):
    amt = 15 * math.sin(2 * math.pi * (t / duration))
    return np.clip(frame + amt, 0, 255).astype(np.uint8)


##############################################
# 12. Contrast Wave
##############################################
def contrast_wave(frame, t, duration):
    factor = 1 + 0.08 * math.sin(2 * math.pi * (t / duration))
    return np.clip((frame - 128) * factor + 128, 0, 255).astype(np.uint8)


##############################################
# 13. Warm Light Glow
##############################################
def warm_light_glow(frame, t, duration):
    amt = int(20 * ease_in_out(t, duration))
    glow = frame.copy().astype(float)
    glow[:, :, 2] += amt
    glow[:, :, 1] += amt // 2
    return np.clip(glow, 0, 255).astype(np.uint8)


##############################################
# 14. Vignette Fade
##############################################
def vignette_fade(frame, t, duration):
    h, w = frame.shape[:2]
    p = ease_in_out(t, duration)

    mask = np.zeros((h, w), np.float32)
    cv2.circle(mask, (w//2, h//2), min(h, w)//2, 1 - p*0.5, -1)
    mask = cv2.GaussianBlur(mask, (201, 201), 0)

    return (frame * mask[..., None]).astype(np.uint8)


##############################################
# 15. Subtle Color Shift
##############################################
def subtle_color_shift(frame, t, duration):
    shift = int(10 * math.sin(2 * math.pi * (t / duration)))
    frame = frame.astype(np.int32)
    frame[:, :, 2] = np.clip(frame[:, :, 2] + shift, 0, 255)
    return frame.astype(np.uint8)
