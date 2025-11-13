from PIL import Image, ImageDraw

# ---------- CONFIG ----------
FINAL_SIZE = (3840, 2160)   # UHD 16:9
pip_original_size = (800, 800)  # approximate PIP native resolution
start_scale = 1.6
end_scale = 0.5
# updated desired end position
x_end_ratio = 0.10   # push further left (10% from left edge)
y_end_ratio = 0.82   # same vertical bottom alignment
# ----------------------------

def draw_mock(position, scale, filename):
    W, H = FINAL_SIZE
    pip_w = int(pip_original_size[0] * scale)
    pip_h = int(pip_original_size[1] * scale)

    pip_x, pip_y = position

    # Convert to top-left corner position (Pillow uses top-left anchors)
    top_left_x = int(pip_x - pip_w / 2)
    top_left_y = int(pip_y - pip_h / 2)

    # Create base canvas
    img = Image.new("RGB", (W, H), (30, 30, 30))
    draw = ImageDraw.Draw(img)

    # Draw border guide
    draw.rectangle([0, 0, W - 1, H - 1], outline=(120, 120, 120), width=4)

    # Draw PIP rectangle
    draw.rectangle(
        [top_left_x, top_left_y, top_left_x + pip_w, top_left_y + pip_h],
        fill=(220, 60, 60),
        outline="white",
        width=6
    )

    # Label the frame
    draw.text((50, 50), filename, fill="white")

    img.save(filename)
    print(f"✅ Saved: {filename}")


# === Define start and end positions ===
W, H = FINAL_SIZE
start_pos = (W / 2, H / 2)                      # exact center
end_pos = (W * x_end_ratio, H * y_end_ratio)    # shifted more left

# === Draw mocks ===
draw_mock(start_pos, start_scale, "intro_start_mock.png")
draw_mock(end_pos, end_scale, "intro_end_mock.png")
