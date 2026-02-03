
import os
import cv2
import numpy as np
from rembg import remove
from PIL import Image, ImageTk, ImageEnhance, ImageFilter
from moviepy.editor import ImageClip, CompositeVideoClip, AudioFileClip, ColorClip, VideoClip, vfx
import random
import tkinter as tk
from tkinter import ttk, Canvas, Frame, Scrollbar

# Reuse caption logic from static clip script
from scripts.clip import split_text_by_time, create_caption_image

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

def generate_single_clip_from_data(fg_pil, bg_pil, choice, audio_path, output_path, audio_text=""):
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
    
    # Base Clips
    bg_clip = ImageClip(np.array(bg_pil), duration=duration)
    fg_clip_static = ImageClip(np.array(fg_pil), transparent=True, duration=duration)
    
    final_clip = None

    # EFFECT LOGIC
    if choice == "1": # Zoom Subject
        fg_clip = create_zooming_clip(fg_pil, duration, max_zoom=1.15)
        fg_clip = fg_clip.set_position(("center", "center"))
        bg_clip = bg_clip.resize(lambda t: 1 + 0.08 * t / duration)
        bg_clip = bg_clip.set_position(("center", "center"))
        final_clip = CompositeVideoClip([bg_clip, fg_clip], size=(video_width, video_height))

    elif choice == "2": # Parallax
        bg_clip_large = bg_clip.resize(1.1)
        bg_clip_anim = bg_clip_large.set_position(lambda t: (-40 * t, "center"))
        fg_clip_anim = fg_clip_static.set_position(lambda t: (40 * t, "center"))
        final_clip = CompositeVideoClip([bg_clip_anim, fg_clip_anim], size=(video_width, video_height))
        
    elif choice == "3": # Floating
        fg_clip = fg_clip_static.set_position(lambda t: ("center", video_height/2 - fg_clip_static.h/2 + 25 * np.sin(2 * np.pi * t / 4)))
        final_clip = CompositeVideoClip([bg_clip, fg_clip], size=(video_width, video_height))
        
    elif choice == "4": # Zoom BG
        bg_clip = bg_clip.resize(lambda t: 1 + 0.2 * t / duration)
        fg_clip = fg_clip_static.set_position(("center", "center"))
        final_clip = CompositeVideoClip([bg_clip, fg_clip], size=(video_width, video_height))
        
    elif choice == "5": # Shake (Glitch)
        # Slower Glitch/Shake
        def make_shake(t):
            import random
            seed = int(t * 6) 
            random.seed(seed)
            x_off = random.randint(-15, 15)
            y_off = random.randint(-15, 15)
            return (video_width/2 - fg_clip_static.w/2 + x_off,
                    video_height/2 - fg_clip_static.h/2 + y_off)
        fg_clip = fg_clip_static.set_position(make_shake)
        final_clip = CompositeVideoClip([bg_clip, fg_clip], size=(video_width, video_height))

    # --- NEW EFFECTS ---

    elif choice == "6": # BW to Color Reveal
        # Fade from Grayscale to Color
        bg_bw = bg_clip.fx(vfx.blackwhite)
        fg_bw = fg_clip_static.fx(vfx.blackwhite)
        
        # Crossfade
        bg_anim = CompositeVideoClip([bg_bw, bg_clip.set_start(0).crossfadein(duration)]).set_duration(duration)
        fg_anim = CompositeVideoClip([fg_bw, fg_clip_static.set_start(0).crossfadein(duration)]).set_duration(duration)
        
        final_clip = CompositeVideoClip([bg_anim, fg_anim], size=(video_width, video_height))

    elif choice == "7": # Sepia Vintage
        def sepia_filter(im):
            # Simple sepia matrix
            sepia_matrix = np.array([[0.393, 0.769, 0.189],
                                     [0.349, 0.686, 0.168],
                                     [0.272, 0.534, 0.131]])
            # Apply to RGB channels
            img_sepia = im.copy()
            img_sepia[:,:,:3] = im[:,:,:3].dot(sepia_matrix.T)
            np.clip(img_sepia, 0, 255, out=img_sepia)
            return img_sepia

        bg_anim = bg_clip.fl_image(sepia_filter)
        fg_anim = fg_clip_static.fl_image(sepia_filter)
        final_clip = CompositeVideoClip([bg_anim, fg_anim], size=(video_width, video_height))

    elif choice == "8": # Blur Focus (BG Blur)
        # Blur BG heavily
        # Pre-compute blurred image to save time
        bg_pil_blur = bg_pil.filter(ImageFilter.GaussianBlur(10))
        bg_clip_blur = ImageClip(np.array(bg_pil_blur), duration=duration)
        
        # Pulse between sharp and blur
        # Simple crossfade for bloom effect
        bg_anim = CompositeVideoClip([
            bg_clip,
            bg_clip_blur.set_start(0).crossfadein(1).crossfadeout(1)
        ]).set_duration(duration)
        
        final_clip = CompositeVideoClip([bg_anim, fg_clip_static], size=(video_width, video_height))

    elif choice == "9": # Flash / Strobe
        # Increased brightness pulses
        def flash_effect(get_frame, t):
            frame = get_frame(t)
            # Pulse factor between 1.0 and 1.5
            factor = 1 + 0.5 * np.sin(10 * t)**2
            return np.clip(frame * factor, 0, 255).astype('uint8')
            
        bg_anim = bg_clip.fl(flash_effect)
        final_clip = CompositeVideoClip([bg_anim, fg_clip_static], size=(video_width, video_height))

    elif choice == "10": # Ghost Hover
        # Main FG + Semi-transparent echo
        ghost = fg_clip_static.set_opacity(0.4).set_start(0.2).set_position(lambda t: ("center", video_height/2 - fg_clip_static.h/2 - 20))
        final_clip = CompositeVideoClip([bg_clip, ghost, fg_clip_static], size=(video_width, video_height))

    elif choice == "11": # Color Cycle (Hue Shift)
        # Creating a hue shift manually is expensive in numpy per frame.
        # Let's do a simple channel shuffle/tint for "Neon" feel
        def color_shift(get_frame, t):
            im = get_frame(t)
            # Shift tint based on time
            shift = int(t * 50) % 255
            # Just tint R channel
            im[:,:,0] = np.clip(im[:,:,0] + shift, 0, 255)
            return im
            
        bg_anim = bg_clip.fl(color_shift)
        final_clip = CompositeVideoClip([bg_anim, fg_clip_static], size=(video_width, video_height))

    elif choice == "12": # Vignette Pulse
        # Create vignette mask
        def make_vignette(t):
            # Pulse opacity
            opacity = 150 + 50 * np.sin(3*t)
            # Create a radial gradient using CV2/Numpy
            Y, X = np.ogrid[:video_height, :video_width]
            center_x, center_y = video_width/2, video_height/2
            dist_from_center = np.sqrt((X - center_x)**2 + (Y - center_y)**2)
            mask = dist_from_center / (np.sqrt(center_x**2 + center_y**2))
            mask = np.clip(mask * (opacity/255.0), 0, 1)
            # Expand to 3 channels for multiplication
            mask_3c = np.dstack([mask]*3) 
            return mask_3c

        # Apply darkening
        def apply_vignette(get_frame, t):
            im = get_frame(t)
            mask = make_vignette(t)
            # Darken edges
            return (im * (1 - mask)).astype('uint8')

        bg_anim = bg_clip.fl(apply_vignette)
        final_clip = CompositeVideoClip([bg_anim, fg_clip_static], size=(video_width, video_height))

    elif choice == "13": # Spotlight (Dark BG)
        bg_dark = bg_clip.fx(vfx.colorx, 0.3) # Darken BG
        # FG normal (popping out)
        final_clip = CompositeVideoClip([bg_dark, fg_clip_static], size=(video_width, video_height))

    elif choice == "14": # Cinematic Bars
        # Animated black bars
        def draw_bars(get_frame, t):
            im = get_frame(t)
            bar_height = int(100 * (t/duration)) if t < 1 else 100 # Animate in
            im[:bar_height, :] = 0
            im[-bar_height:, :] = 0
            return im
            
        final_clip = CompositeVideoClip([bg_clip, fg_clip_static], size=(video_width, video_height))
        # Apply filter to whole comp
        final_clip = final_clip.fl(draw_bars)

    elif choice == "15": # Mirror Reflection
        # Flip FG vertical
        reflection = fg_clip_static.fx(vfx.mirror_y)
        # Position below
        reflection = reflection.set_position(lambda t: ("center", video_height/2 + fg_clip_static.h/2 - 20))
        reflection = reflection.set_opacity(0.3)
        # Apply
        final_clip = CompositeVideoClip([bg_clip, reflection, fg_clip_static], size=(video_width, video_height))

    else: # Skip/Default
        # Just return basic
        return False

    # ---- ADD SUBTITLES ----
    if audio_text:
        subtitles = split_text_by_time(audio_text, duration, max_chars=42)
        subtitle_clips = []
        for text, start, end in subtitles:
            img = create_caption_image(text, video_width)
            txt = (
                ImageClip(img, transparent=True)
                .set_position(("center", video_height - 100)) # Bottom
                .set_start(start)
                .set_end(end)
            )
            subtitle_clips.append(txt)
        
        # Add to composition
        if subtitle_clips:
            # We must reform the CompositeVideoClip to include subtitles
            # final_clip is already a CVC, we can grab its clips list
            # But safer to just wrap it
            final_clip = CompositeVideoClip(final_clip.clips + subtitle_clips, size=(video_width, video_height))

    final_clip = final_clip.set_audio(audio)
    
    # Write File
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

        # Header Frame
        header_frame = Frame(root, padx=20, pady=10)
        header_frame.pack(fill="x")
        
        lbl_title = tk.Label(header_frame, text="Select Effects for All Scenes", font=("Arial", 16, "bold"))
        lbl_title.pack(side="left")
        
        btn_run = tk.Button(header_frame, text="GENERATE ALL VIDEOS", font=("Arial", 12, "bold"), 
                            bg="#4CAF50", fg="white", padx=20, pady=5, 
                            command=self.on_generate)
        btn_run.pack(side="right")

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
        
        # 3. Controls (Updated with 15 options)
        ctrl_frame = Frame(row_frame)
        ctrl_frame.pack(side="left", padx=30, fill="y")
        
        choice_var = tk.StringVar(value="1") # Default Zoom
        self.choices[data['id']] = choice_var
        
        tk.Label(ctrl_frame, text="Select Effect:", font=("Arial", 10, "bold")).pack(anchor="w")
        
        # Two columns of options
        cols_frame = Frame(ctrl_frame)
        cols_frame.pack(anchor="w")
        
        col1 = Frame(cols_frame)
        col1.pack(side="left", padx=10, anchor="n")
        col2 = Frame(cols_frame)
        col2.pack(side="left", padx=10, anchor="n")

        options = [
            ("1. Zoom Subject", "1"),
            ("2. Parallax", "2"),
            ("3. Floating (Bob)", "3"),
            ("4. Zoom BG", "4"),
            ("5. Shake (Glitch)", "5"),
            ("6. BW to Color", "6"),
            ("7. Sepia Vintage", "7"),
            ("8. Blur Focus", "8"),
            ("9. Flash Strobe", "9"),
            ("10. Ghost Hover", "10"),
            ("11. Color Cycle", "11"),
            ("12. Vignette Pulse", "12"),
            ("13. Spotlight", "13"),
            ("14. Cinematic Bars", "14"),
            ("15. Mirror Reflect", "15"),
            ("Skip (Static)", "0")
        ]
        
        for i, (text, val) in enumerate(options):
            parent = col1 if i < 8 else col2
            tk.Radiobutton(parent, text=text, variable=choice_var, value=val, font=("Arial", 10)).pack(anchor="w")

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
            "output_path": scene['output_path'],
            "audio_text": scene.get('audio_text', '') # Pass text for subtitles
        })
        
    print("[BATCH] Extraction complete. Launching UI...")
    
    # 2. Launch UI
    root = tk.Tk()
    app = BatchVerificationApp(root, prepared_data)
    root.mainloop()
    
    # Get results from app (app.result_map)
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
            continue
            
        success = generate_single_clip_from_data(
            data['fg_pil'], 
            data['bg_pil'], 
            choice, 
            data['audio_path'], 
            data['output_path'],
            data['audio_text']
        )
        
        if success:
             print(f"  -> Scene {sid} Generated Successfully.")
        else:
             print(f"  -> Scene {sid} generation skipped/failed.")

    print("\n[BATCH] All rendering complete.")
    return True
