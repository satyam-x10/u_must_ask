import cv2
import numpy as np
import os
from tqdm import tqdm
import subprocess

input_folder = "video"
output_folder = "output_circle_videos"
temp_frames = "temp_frames"
os.makedirs(output_folder, exist_ok=True)
os.makedirs(temp_frames, exist_ok=True)

video_files = [f for f in os.listdir(input_folder) if f.lower().endswith(('.mp4', '.mov', '.avi', '.mkv', '.webm'))]

for video_name in tqdm(video_files, desc="Processing videos"):
    input_path = os.path.join(input_folder, video_name)
    base_name = os.path.splitext(video_name)[0]
    frame_dir = os.path.join(temp_frames, base_name)
    os.makedirs(frame_dir, exist_ok=True)

    cap = cv2.VideoCapture(input_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    size = min(width, height)
    radius = size // 2

    mask = np.zeros((size, size, 4), dtype=np.uint8)
    cv2.circle(mask, (radius, radius), radius, (255, 255, 255, 255), -1)

    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        y = (height - size) // 2
        x = (width - size) // 2
        square_frame = frame[y:y + size, x:x + size]
        square_frame = cv2.cvtColor(square_frame, cv2.COLOR_BGR2BGRA)
        square_frame[mask[:, :, 3] == 0] = (0, 0, 0, 0)

        frame_path = os.path.join(frame_dir, f"{frame_idx:05d}.png")
        cv2.imwrite(frame_path, square_frame)
        frame_idx += 1

    cap.release()

    # Combine frames into transparent video with ffmpeg
    output_path = os.path.join(output_folder, f"{base_name}_circle.webm")
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-framerate", str(int(fps)),
        "-i", os.path.join(frame_dir, "%05d.png"),
        "-c:v", "libvpx-vp9",
        "-pix_fmt", "yuva420p",
        output_path
    ]
    subprocess.run(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Cleanup temporary frames
    for f in os.listdir(frame_dir):
        os.remove(os.path.join(frame_dir, f))
    os.rmdir(frame_dir)

print("✅ All videos cropped into circles with transparent backgrounds and saved as .webm files.")
