import os
from scripts.thumbnail import create_clickbait_thumbnail

def generate_thumbnails(title_id, title_name):
    bg_path = f"outputs/thumbnails/thumb_{title_id}.png"   
    cat_path = "static/img/cat-exc.png"
    box_path = "static/img/comment_box.png"
    output_path = f"outputs/thumbnails/thumbnail_{title_id}.png"

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    create_clickbait_thumbnail(bg_path, cat_path, box_path, title_name, output_path)