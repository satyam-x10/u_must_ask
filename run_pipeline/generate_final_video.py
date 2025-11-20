import os
import re
import numpy as np
from moviepy.editor import (
    VideoFileClip, concatenate_videoclips,
    CompositeVideoClip, ColorClip, ImageClip
)
from moviepy.video.fx.crop import crop


def make_circle_mask(size, feather=2):
    h, w = size
    y, x = np.ogrid[:h, :w]
    cy, cx = h / 2, w / 2
    r = min(cx, cy)

    dist = np.sqrt((x - cx)**2 + (y - cy)**2)
    mask = (dist <= r).astype(float)

    edge = (dist > r - feather) & (dist < r + feather)
    mask[edge] = (1 - (dist[edge] - (r - feather)) / (2 * feather)).clip(0, 1)

    return mask


def generate_final_video(filepath_to_script: str):
    script_id = os.path.basename(filepath_to_script).replace("script_", "").replace(".json", "")
    BASE = "outputs"

    clips_dir = os.path.join(BASE, "clips", script_id)
    videos_dir = os.path.join(BASE, "videos")
    os.makedirs(videos_dir, exist_ok=True)

    output_path = os.path.join(videos_dir, f"{script_id}.mp4")

    # ------------------------------------------------------------------------------------
    # LOAD INTRO + OUTRO CLIPS
    # ------------------------------------------------------------------------------------
    intro_path = os.path.join(clips_dir, "intro.mp4")
    outro_path = os.path.join(clips_dir, "outro.mp4")

    intro_clip = VideoFileClip(intro_path) if os.path.exists(intro_path) else None
    outro_clip = VideoFileClip(outro_path) if os.path.exists(outro_path) else None

    # ------------------------------------------------------------------------------------
    # GET MAIN VIDEO CLIPS
    # ------------------------------------------------------------------------------------
    def extract_num(path):
        nums = re.findall(r'\d+', os.path.basename(path))
        return int(nums[0]) if nums else 0

    video_files = sorted(
        [
            os.path.join(clips_dir, f)
            for f in os.listdir(clips_dir)
            if f.endswith(".mp4") and f not in ["intro.mp4", "outro.mp4"]
        ],
        key=extract_num
    )

    if not video_files:
        print("No video clips found:", clips_dir)
        return None

    clips = [VideoFileClip(v) for v in video_files]
    base = concatenate_videoclips(clips, method="compose")

    # ------------------------------------------------------------------------------------
    # PiP OVERLAY (dog.mp4)
    # ------------------------------------------------------------------------------------
    pip = VideoFileClip("static/vid/dog.mp4")

    pip_size = 110
    side = min(pip.w, pip.h)

    pip = crop(
        pip,
        x_center=pip.w / 2,
        y_center=pip.h / 2,
        width=side,
        height=side
    ).resize(width=pip_size)

    mask_array = make_circle_mask((pip_size, pip_size), feather=2)
    pip_mask = ImageClip(mask_array, ismask=True).set_duration(pip.duration)
    pip = pip.set_mask(pip_mask)

    border_size = pip_size + 12
    border_mask_arr = make_circle_mask((border_size, border_size), feather=2)
    border_mask = ImageClip(border_mask_arr, ismask=True).set_duration(pip.duration)

    border = ColorClip((border_size, border_size), color=(255, 255, 255))
    border = border.set_mask(border_mask).set_duration(pip.duration)

    margin = 30
    pip_pos = (margin, base.h - pip_size - margin)
    border_pos = (pip_pos[0] - 6, pip_pos[1] - 6)

    base_with_pip = CompositeVideoClip(
        [
            base,
            border.set_position(border_pos).set_end(pip.duration),
            pip.set_position(pip_pos).set_end(pip.duration)
        ],
        size=base.size
    )

    # ------------------------------------------------------------------------------------
    # MERGE INTRO + MAIN + OUTRO
    # ------------------------------------------------------------------------------------
    timeline = []

    if intro_clip:
        timeline.append(intro_clip)

    timeline.append(base_with_pip)

    if outro_clip:
        timeline.append(outro_clip)

    final = concatenate_videoclips(timeline, method="compose")

    # ------------------------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------------------------
    final.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=24)

    base.close()
    pip.close()
    base_with_pip.close()
    final.close()

    if intro_clip: intro_clip.close()
    if outro_clip: outro_clip.close()

    print("Saved:", output_path)
    return output_path
