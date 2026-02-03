
import os
import cv2
import numpy as np
from rembg import remove
from PIL import Image, ImageTk
from moviepy.editor import ImageClip, CompositeVideoClip, AudioFileClip, ColorClip, VideoClip
import random
import tkinter as tk
from tkinter import ttk, Canvas, Frame, Scrollbar

# Keep existing helper functions
def extract_layers(image_path):
    """
    Extracts foreground and background from an image.
    Returns:
        fg_pil (PIL.Image): RGBA foreground image.
        bg_pil (PIL.Image): RGB inpainted background image.
        original_pil (PIL.Image): Original image for review.
    """
    print(f"  -> Extracting layers for {os.path.basename(image_path)}...")
    input_image = Image.open(image_path)
    
    # 1. Remove background using rembg
    fg_pil = remove(input_image)
    
    # 2. Create Mask for Inpainting
    fg_np = np.array(fg_pil)
    alpha = fg_np[:, :, 3]
    # Dilate mask slightly to ensure clean edges for inpainting
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.dilate(alpha, kernel, iterations=2)
    
    # 3. Inpaint Background using OpenCV
    img_np = np.array(input_image.convert("RGB"))
    # cv2.inpaint requires BGR image and single channel mask
    img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    
    # Radius 3, NS method
    inpainted_bgr = cv2.inpaint(img_bgr, mask, 3, cv2.INPAINT_TELEA)
    inpainted_rgb = cv2.cvtColor(inpainted_bgr, cv2.COLOR_BGR2RGB)
    
    bg_pil = Image.fromarray(inpainted_rgb)
    
    return fg_pil, bg_pil, input_image

def create_zooming_clip(pil_image_rgba, duration, max_zoom=1.05):
    """
    Creates a VideoClip that zooms the image using PIL to preserve Alpha channel correctness.
    Returns: VideoClip (RGBA)
    """
    w, h = pil_image_rgba.size
    
    def make_frame(t):
        progress = t / duration 
        # Calculate current scale
        scale = 1.0 + (max_zoom - 1.0) * progress
        
        new_w = int(w * scale)
        new_h = int(h * scale)
        
        # Resize using PIL
        resized = pil_image_rgba.resize((new_w, new_h), Image.Resampling.BILINEAR)
        return np.array(resized)

    # Create clip that returns RGBA
    clip = VideoClip(make_frame, duration=duration)
    
    # Separate Mask for MoviePy
    def make_mask(t):
        frame = make_frame(t)
        return frame[:, :, 3] / 255.0
        
    mask_clip = VideoClip(make_mask, duration=duration, ismask=True)
    
    # Create RGB clip
    def make_rgb(t):
        frame = make_frame(t)
        return frame[:, :, :3]
        
    rgb_clip = VideoClip(make_rgb, duration=duration)
    rgb_clip = rgb_clip.set_mask(mask_clip)
    
    return rgb_clip

def generate_single_clip_from_data(fg_pil, bg_pil, choice, audio_path, output_path):
    """
    Generates a single clip based on pre-calculated assets and choice.
    """
    video_width = 1920
    video_height = 1080
    
    audio = AudioFileClip(audio_path)
    duration = audio.duration
    
    # Resize Logic
    fg_pil = fg_pil.resize((video_width, video_height), Image.Resampling.LANCZOS)
    bg_pil = bg_pil.resize((video_width, video_height), Image.Resampling.LANCZOS)
    
    bg_clip = ImageClip(np.array(bg_pil), duration=duration)
    fg_clip_static = ImageClip(np.array(fg_pil), transparent=True, duration=duration)
    
    final_clip = None

    if choice == "1": # Zoom Subject
        # INCREASED: max_zoom 1.15
        fg_clip = create_zooming_clip(fg_pil, duration, max_zoom=1.15)
        fg_clip = fg_clip.set_position(("center", "center"))
        # INCREASED BG: 0.08
        bg_clip = bg_clip.resize(lambda t: 1 + 0.08 * t / duration)
        bg_clip = bg_clip.set_position(("center", "center"))
        final_clip = CompositeVideoClip([bg_clip, fg_clip], size=(video_width, video_height))

    elif choice == "2": # Parallax
        bg_clip_large = bg_clip.resize(1.1)
        # INCREASED: Speed 40
        bg_clip_anim = bg_clip_large.set_position(lambda t: (-40 * t, "center"))
        # INCREASED: Speed 40
        fg_clip_anim = fg_clip_static.set_position(lambda t: (40 * t, "center"))
        final_clip = CompositeVideoClip([bg_clip_anim, fg_clip_anim], size=(video_width, video_height))
        
    elif choice == "3": # Floating
        # INCREASED: Amplitude 25
        fg_clip = fg_clip_static.set_position(lambda t: ("center", video_height/2 - fg_clip_static.h/2 + 25 * np.sin(2 * np.pi * t / 4)))
        final_clip = CompositeVideoClip([bg_clip, fg_clip], size=(video_width, video_height))
        
    elif choice == "4": # Zoom BG
        # INCREASED: Zoom 0.2
        bg_clip = bg_clip.resize(lambda t: 1 + 0.2 * t / duration)
        fg_clip = fg_clip_static.set_position(("center", "center"))
        final_clip = CompositeVideoClip([bg_clip, fg_clip], size=(video_width, video_height))
        
    elif choice == "5": # Shake (Jitter)
        # Slower Glitch/Shake
        # Update random offset only every 0.15 seconds (~6-7 times a second)
        def make_shake(t):
            import random
            # Seed based on time buckets to hold position for a few frames
            seed = int(t * 6) 
            random.seed(seed)
            
            x_off = random.randint(-15, 15)
            y_off = random.randint(-15, 15)
            
            return (video_width/2 - fg_clip_static.w/2 + x_off,
                    video_height/2 - fg_clip_static.h/2 + y_off)
                    
        fg_clip = fg_clip_static.set_position(make_shake)
        final_clip = CompositeVideoClip([bg_clip, fg_clip], size=(video_width, video_height))

    else: # SKIP or Default
        # Just return basic
        return False

    final_clip = final_clip.set_audio(audio)
    final_clip.write_videofile(
        output_path, fps=24, codec="libx264", audio_codec="aac", threads=4, logger=None
    )
    return True


# ==================================================================================
# BATCH UI CLASS
# ==================================================================================

class BatchVerificationApp:
    def __init__(self, root, scene_data_list):
        self.root = root
        self.root.title("Batch Effect Verification")
        self.root.geometry("1400x900") # WIDER window
        
        self.scene_data_list = scene_data_list
        self.choices = {} # scene_id -> StringVar
        self.thumbnails = [] # Keep refs to prevent GC

        # Header
        header = tk.Label(root, text="Select Effects for All Scenes", font=("Arial", 16, "bold"))
        header.pack(pady=10)

        # Container for Canvas + Scrollbars
        container = Frame(root)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        self.canvas = Canvas(container)
        self.v_scroll = Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.h_scroll = Scrollbar(container, orient="horizontal", command=self.canvas.xview)
        
        self.scrollable_frame = Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        self.canvas.configure(yscrollcommand=self.v_scroll.set, xscrollcommand=self.h_scroll.set)

        self.v_scroll.pack(side="right", fill="y")
        self.h_scroll.pack(side="bottom", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Populate Rows
        for i, data in enumerate(scene_data_list):
            self.create_row(i, data)

        # Footer Buttons
        footer = Frame(root,  bg="#f0f0f0", height=80)
        footer.pack(side="bottom", fill="x")
        
        btn_run = tk.Button(footer, text="GENERATE ALL VIDEOS", font=("Arial", 14, "bold"), 
                            bg="#4CAF50", fg="white", padx=20, pady=10, 
                            command=self.on_generate)
        btn_run.pack(pady=20)
        
        # Mousewheel scroll vertical
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def create_row(self, index, data):
        row_frame = Frame(self.scrollable_frame, bd=2, relief="groove", padx=10, pady=10)
        row_frame.pack(fill="x", padx=10, pady=5, anchor="w") # Anchor west

        
        # 1. Info
        info_frame = Frame(row_frame, width=100)
        info_frame.pack(side="left", padx=10)
        tk.Label(info_frame, text=f"Scene {data['id']}", font=("Arial", 12, "bold")).pack()
        
        # 2. Images (Original vs Cutout)
        # Resize for thumbnail
        thumb_h = 150
        
        # Original
        orig_pil = data['original_pil']
        orig_ratio = orig_pil.width / orig_pil.height
        orig_thumb = orig_pil.resize((int(thumb_h * orig_ratio), thumb_h))
        orig_tk = ImageTk.PhotoImage(orig_thumb)
        self.thumbnails.append(orig_tk) # Keep ref
        
        lbl_orig = tk.Label(row_frame, image=orig_tk)
        lbl_orig.pack(side="left", padx=5)
        
        # Cutout (FG)
        fg_pil = data['fg_pil']
        fg_thumb = fg_pil.resize((int(thumb_h * orig_ratio), thumb_h))
        
        # Compose FG over checkerboard for visibility
        bg_check = Image.new("RGB", fg_thumb.size, (200, 200, 200)) # Simple grey for UI
        bg_check.paste(fg_thumb, (0, 0), fg_thumb)
        
        fg_tk = ImageTk.PhotoImage(bg_check)
        self.thumbnails.append(fg_tk)
        
        lbl_fg = tk.Label(row_frame, image=fg_tk)
        lbl_fg.pack(side="left", padx=5)
        
        # 3. Controls
        ctrl_frame = Frame(row_frame)
        ctrl_frame.pack(side="left", padx=30, fill="y")
        
        choice_var = tk.StringVar(value="1") # Default Zoom
        self.choices[data['id']] = choice_var
        
        tk.Label(ctrl_frame, text="Select Effect:", font=("Arial", 10, "bold")).pack(anchor="w")
        
        options = [
            ("1. Zoom Subject", "1"),
            ("2. Parallax (Move)", "2"),
            ("3. Floating (Bob)", "3"),
            ("4. Zoom Background", "4"),
            ("5. Shake (Glitch)", "5"),
            ("Skip (Static)", "0")
        ]
        
        for text, val in options:
            tk.Radiobutton(ctrl_frame, text=text, variable=choice_var, value=val, font=("Arial", 10)).pack(anchor="w")


    def on_generate(self):
        # Gather choices
        self.result_map = {}
        for sid, var in self.choices.items():
            self.result_map[sid] = var.get()
        self.root.destroy()


def run_batch_processor(scenes_to_process):
    """
    Main entry point for batch processing.
    scenes_to_process: list of dicts {id, image_path, audio_path, output_path, audio_text}
    """
    
    # 1. Pre-process (Extract Layers)
    print("\n[BATCH] Starting Pre-processing (Extraction)... this may take a minute.")
    prepared_data = []
    
    for scene in scenes_to_process:
        print(f"Processing Scene {scene['id']}...")
        fg, bg, orig = extract_layers(scene['image_path'])
        
        prepared_data.append({
            "id": scene['id'],
            "fg_pil": fg,
            "bg_pil": bg,
            "original_pil": orig,
            "image_path": scene['image_path'],
            "audio_path": scene['audio_path'],
            "output_path": scene['output_path']
        })
        
    print("[BATCH] Extraction complete. Launching UI...")
    
    # 2. Launch UI
    root = tk.Tk()
    app = BatchVerificationApp(root, prepared_data)
    root.mainloop()
    
    # Get results from app (app.result_map)
    # If window closed without running, result_map might not exist
    if not hasattr(app, 'result_map'):
        print("[BATCH] UI closed without generating.")
        return
        
    choices = app.result_map
    
    # 3. Generate Videos
    print("\n[BATCH] UI Completed. Starting Rendering...")
    
    for data in prepared_data:
        sid = data['id']
        choice = choices.get(sid, "0")
        
        print(f"Rendering Scene {sid} (Effect: {choice})...")
        
        if choice == "0":
            print(f"  -> Skipping interactive effect (Static).")
            # We return false/skip here, caller logic handles fallback? 
            # Actually caller logic expects us to generate ONE file. 
            # If we skip, we generate nothing, and caller (generate_all_clips) does fallback?
            # Let's handle fallback inside generate_all_clips if this returns False.
            continue
            
        success = generate_single_clip_from_data(
            data['fg_pil'], 
            data['bg_pil'], 
            choice, 
            data['audio_path'], 
            data['output_path']
        )
        
        if success:
             print(f"  -> Scene {sid} Generated Successfully.")
        else:
             print(f"  -> Scene {sid} generation skipped/failed.")

    print("\n[BATCH] All rendering complete.")
    return True
