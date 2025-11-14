import os
import time
from PIL import Image
import torch
from diffusers import KandinskyPriorPipeline, KandinskyPipeline

# ==============================
#   SAFE CPU THREAD SETTINGS
# ==============================
os.environ["OMP_NUM_THREADS"] = "2"
os.environ["MKL_NUM_THREADS"] = "2"
os.environ["OPENBLAS_NUM_THREADS"] = "2"
os.environ["VECLIB_MAXIMUM_THREADS"] = "2"
os.environ["NUMEXPR_NUM_THREADS"] = "2"

torch.set_num_threads(2)
torch.set_num_interop_threads(2)

# ==============================
#   LOAD KANDINSKY MODELS
# ==============================
prior = KandinskyPriorPipeline.from_pretrained(
    "kandinsky-community/kandinsky-2-1-prior",
    torch_dtype=torch.float32
).to("cpu")

pipe = KandinskyPipeline.from_pretrained(
    "kandinsky-community/kandinsky-2-1",
    torch_dtype=torch.float32
).to("cpu")

# ==============================
#   MAIN FUNCTION
# ==============================
def generate_image(prompt: str):
    if not prompt.strip():
        raise ValueError("Prompt cannot be empty.")

    # Add cartoon style
    prompt = "A cartoon style image of " + prompt

    # Output folder
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)

    # Auto filename
    filename = prompt[:40].replace(" ", "_").replace("/", "") + ".png"
    output_path = os.path.join(output_dir, filename)

    print(f"\nGenerating: {prompt[:60]}...")
    t0 = time.time()

    # Get embeddings
    image_embeds, neg_embeds = prior(prompt).to_tuple()

    # Generate image
    result = pipe(
        prompt=prompt,
        image_embeds=image_embeds,
        negative_image_embeds=neg_embeds,
        num_inference_steps=10,
        height=360,
        width=640
    )

    image = result.images[0]
    image.save(output_path)

    print(f"Saved → {output_path} ({round(time.time() - t0, 1)}s)")
    return output_path


if __name__ == "__main__":
    test_prompt = (
        "a minimal cartoon-style emblem featuring a large question mark at the center, "
        "floating in a clean sky with soft clouds, no characters or faces, simple shapes, "
        "blue and white color palette, subtle tech and knowledge theme, perfect for a "
        "YouTube channel called 'One Random Question'"
    )
    generate_image(test_prompt)
