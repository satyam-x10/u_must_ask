import cv2
from rembg import remove
from PIL import Image
from tqdm import tqdm
import os

input_video = "bird.mp4"
output_dir = "frames"
os.makedirs(output_dir, exist_ok=True)

cap = cv2.VideoCapture(input_video)
frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

for i in tqdm(range(frame_count)):
    ret, frame = cap.read()
    if not ret:
        break
    print(f"Processing frame {i+1}/{frame_count}")
    # Convert OpenCV (BGR) → PIL (RGB)
    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    output = remove(img)  # background removal
    
    output.save(f"{output_dir}/frame_{i:04d}.png")

cap.release()
