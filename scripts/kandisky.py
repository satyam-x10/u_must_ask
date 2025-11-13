import os
import time
from PIL import Image, ImageDraw ,ImageFont
import random

import torch
from diffusers import KandinskyPriorPipeline, KandinskyPipeline

def generate_image_from_prompt(prompt: str, output_path: str,text: str) :
   
    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty.")

    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    print(f"\n🖼️ Generating image for prompt: {prompt[:60]}...")
    t0 = time.time()

    # -------------------------------------------------
    # Placeholder image — replace with actual Kandinsky
    # -------------------------------------------------
    # Example Kandinsky usage (uncomment after enabling model):
    prior = KandinskyPriorPipeline.from_pretrained(
        "kandinsky-community/kandinsky-2-1-prior",
        torch_dtype=torch.float32
    )
    pipe = KandinskyPipeline.from_pretrained(
        "kandinsky-community/kandinsky-2-1",
        torch_dtype=torch.float32
    )
    prior.to("cpu")
    pipe.to("cpu")

    prompt = "A kurzegast style image of " + prompt
    
    image_embeds, negative_image_embeds = prior(prompt).to_tuple()

    image = pipe(
        prompt=prompt,
        image_embeds=image_embeds,
        negative_image_embeds=negative_image_embeds,
        num_inference_steps=20,
        height=720,
        width=1280
    ).images[0]

    
    image.save(output_path)

    # Temporary blank image (for testing)
    # Create base image (black background)
    # width, height = 1280, 720
    # image = Image.new("RGB", (width, height), (0, 0, 0))
    # draw = ImageDraw.Draw(image)

    # # Draw random lines for visual randomness
    # for _ in range(random.randint(5, 15)):  # random number of lines
    #     x1, y1 = random.randint(0, width), random.randint(0, height)
    #     x2, y2 = random.randint(0, width), random.randint(0, height)
    #     color = tuple(random.randint(0, 255) for _ in range(3))
    #     draw.line((x1, y1, x2, y2), fill=color, width=random.randint(1, 5))

    # # write the prompt text on the image increase font size
    # font = ImageFont.truetype("arial.ttf", size=20)
    # draw.text((10, 10), text, fill=(255, 255, 255), font=font)

    # Save the image
    # image.save(output_path)

    print(f"✅ Image saved: {output_path} (in {round(time.time() - t0, 1)}s)")
    return output_path

