import json, os, sys
from moviepy import (
    ImageClip,
    TextClip,
    CompositeVideoClip
)
from pydub import AudioSegment

# ---------- CONFIG ----------
FRAME_W, FRAME_H = 1280, 720
IMAGE_SCALE = 1.1
ZOOM_AMOUNT = 0.03
FONT = "C:/Windows/Fonts/arial.ttf"
NAME_SIZE = 40
TEXT_SIZE = 32
NAME_COLOR = "yellow"
TEXT_COLOR = "white"
TEXT_BG = "#00000080"  # semi-transparent black

AUDIO_FOLDER = "outputs/audio"
VIDEO_OUTPUT_FOLDER = "outputs/video_silent"
# ----------------------------

os.makedirs(VIDEO_OUTPUT_FOLDER, exist_ok=True)


def safe_load_json(path):
    if not os.path.exists(path):
        sys.exit(f"Missing JSON: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_audio_duration(path):
    """Return duration in seconds of an audio file."""
    if not os.path.exists(path):
        sys.exit(f"Missing audio file: {path}")
    try:
        audio = AudioSegment.from_wav(path)
        return len(audio) / 1000.0
    except Exception as e:
        sys.exit(f"Error reading WAV {path}: {e}")


def main():
    print("Loading data...")
    lines = safe_load_json("script.json")
    chars_data = safe_load_json("characters.json")
    chars = {str(c["character_id"]): c for c in chars_data}
    print(f"Loaded {len(lines)} lines, {len(chars)} characters.\n")

    for idx, item in enumerate(lines):
        cid = str(item["person_id"])
        text = item["statement"]
        char = chars.get(cid)

        if not char:
            print(f"⚠️ Skipping line {idx+1}: character {cid} not found.")
            continue

        img_path = char["image"]
        if not os.path.isfile(img_path):
            print(f"⚠️ Skipping line {idx+1}: image not found {img_path}")
            continue

        audio_path = os.path.join(AUDIO_FOLDER, f"line_{idx+1}.wav")
        if not os.path.exists(audio_path):
            print(f"⚠️ Skipping line {idx+1}: audio missing {audio_path}")
            continue

        # --- Duration from audio ---
        dur = get_audio_duration(audio_path)

        # --- Base image clip ---
        img = ImageClip(img_path).with_duration(dur)
        img = img.resized(width=int(FRAME_W * IMAGE_SCALE))

        start_zoom, end_zoom = 1.0, 1.0 + ZOOM_AMOUNT

        def zoom(t):
            f = start_zoom + (end_zoom - start_zoom) * (t / img.duration)
            return (int(img.w * f), int(img.h * f))

        moving = img.resized(zoom)
        moving = moving.with_position(
            lambda t: (-int((moving.w - FRAME_W) / 2), -int((moving.h - FRAME_H) / 2))
        )

        # --- Text overlays ---
        name_clip = (
            TextClip(text=char["name"], font=FONT, font_size=NAME_SIZE, color=NAME_COLOR)
            .with_position((50, 40))
            .with_duration(dur)
        )

        text_clip = (
            TextClip(
                text=text,
                font=FONT,
                font_size=TEXT_SIZE,
                color=TEXT_COLOR,
                bg_color=TEXT_BG,
                size=(int(FRAME_W * 0.9), None),
                method="caption",
            )
            .with_position(("center", FRAME_H - 160))
            .with_duration(dur)
        )

        # --- Combine image + text ---
        scene = CompositeVideoClip([moving, name_clip, text_clip]).with_duration(dur)

        # --- Output filename ---
        out_path = os.path.join(VIDEO_OUTPUT_FOLDER, f"line_{idx+1}.mp4")

        print(f"🎬 Rendering silent line {idx+1}: {char['name']} — {dur:.2f}s")
        scene.write_videofile(
            out_path,
            fps=24,
            codec="libx264",
            audio=False,  # <<--- No audio output
            threads=4,
            preset="medium",
        )

        print(f"✅ Saved {out_path}\n")

    print("🎉 All silent caption videos generated!")


if __name__ == "__main__":
    main()
