import os
import time
from PIL import Image, ImageDraw, ImageFont

import torch
from diffusers import KandinskyPriorPipeline, KandinskyPipeline

prior = KandinskyPriorPipeline.from_pretrained(
        "kandinsky-community/kandinsky-2-1-prior",
        torch_dtype=torch.float32
)
pipe = KandinskyPipeline.from_pretrained(
        "kandinsky-community/kandinsky-2-1",
        torch_dtype=torch.float32
)

def generate_image_from_prompt(prompt: str, output_path: str, text: str):
    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty.")

    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    print(f"\nGenerating image for prompt: {prompt[:60]}...")
    t0 = time.time()

    torch.set_num_threads(2)
    torch.set_num_interop_threads(2)

    # ============================================================
    # Kandinsky model
    # ============================================================
    

    prior.to("cpu")
    pipe.to("cpu")

    # This re-uses the 'prompt' variable from the function input
    prompt = "A cartoon style image of " + prompt

    image_embeds, negative_image_embeds = prior(prompt).to_tuple()

    image = pipe(
        prompt=prompt,
        image_embeds=image_embeds,
        negative_image_embeds=negative_image_embeds,
        num_inference_steps=10,
        height=720,
        width=1280
    ).images[0]


    # Optional: draw text overlay
    draw = ImageDraw.Draw(image)
    try:
        # Ensure you have 'arial.ttf' or specify a different font
        font = ImageFont.truetype("arial.ttf", size=24)
    except:
        font = ImageFont.load_default()

    draw.text((10, 10), text, fill=(255, 255, 255), font=font)

    image.save(output_path)

    print(f"Image saved: {output_path} (in {round(time.time() - t0, 1)}s)")
    return output_path