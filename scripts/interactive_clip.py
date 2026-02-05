
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
from scripts.clip import split_text_by_time, create_caption_image, create_collage

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
        
    elif choice == "5": # Rotate (New)
        # Continuous slow rotation (approx 15 deg/sec)
        # We must re-center after rotation because dimensions change
        rot_func = lambda t: -15 * t 
        fg_clip = fg_clip_static.rotate(rot_func).set_position("center")
        final_clip = CompositeVideoClip([bg_clip, fg_clip], size=(video_width, video_height))

    elif choice == "6": # BW to Color Reveal
        # Fade from Grayscale to Color
        bg_bw = bg_clip.fx(vfx.blackwhite)
        fg_bw = fg_clip_static.fx(vfx.blackwhite)
        
        # Crossfade
        bg_anim = CompositeVideoClip([bg_bw, bg_clip.set_start(0).crossfadein(duration)]).set_duration(duration)
        fg_anim = CompositeVideoClip([fg_bw, fg_clip_static.set_start(0).crossfadein(duration)]).set_duration(duration)
        
        final_clip = CompositeVideoClip([bg_anim, fg_anim], size=(video_width, video_height))

    # REMOVED Sepia (7)
    # REMOVED Blur (8)

    elif choice == "7": # Flash / Strobe (Was 9)
        # Increased brightness pulses
        def flash_effect(get_frame, t):
            frame = get_frame(t)
            # Pulse factor between 1.0 and 1.5
            factor = 1 + 0.5 * np.sin(10 * t)**2
            return np.clip(frame * factor, 0, 255).astype('uint8')
            
        bg_anim = bg_clip.fl(flash_effect)
        final_clip = CompositeVideoClip([bg_anim, fg_clip_static], size=(video_width, video_height))

    # REMOVED Ghost (10)
    # REMOVED Color Cycle (11)

    elif choice == "8": # Vignette Pulse (Was 12)
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

    elif choice == "9": # Spotlight (Was 13)
        bg_dark = bg_clip.fx(vfx.colorx, 0.3) # Darken BG
        # FG normal (popping out)
        final_clip = CompositeVideoClip([bg_dark, fg_clip_static], size=(video_width, video_height))

    elif choice == "10": # Tilt Left/Right
        # Rocking motion (+- 5 degrees)
        rot_func = lambda t: 5 * np.sin(2.5 * t)
        fg_clip = fg_clip_static.rotate(rot_func).set_position("center")
        final_clip = CompositeVideoClip([bg_clip, fg_clip], size=(video_width, video_height))

    elif choice == "11": # Left/Right Movement
        # Slide back and forth
        def move_lr(t):
            offset = 40 * np.sin(2 * t)
            return (video_width/2 - fg_clip_static.w/2 + offset,
                    video_height/2 - fg_clip_static.h/2)
        fg_clip = fg_clip_static.set_position(move_lr)
        final_clip = CompositeVideoClip([bg_clip, fg_clip], size=(video_width, video_height))

    elif choice == "12": # Invisible to Visible (Fade In)
        # Fade in over 1.5 seconds (or full duration if short)
        fade_dur = min(1.5, duration)
        fg_clip = fg_clip_static.crossfadein(fade_dur)
        final_clip = CompositeVideoClip([bg_clip, fg_clip], size=(video_width, video_height))

    # REMOVED Cinematic Bars (14)

    else: # Skip/Default
        # Just return basic
        return False

    # ---- ADD SUBTITLES ----
    if audio_text:
        subtitles = split_text_by_time(audio_text, duration, max_chars=42)
        subtitle_clips = []
        for text, start, end in subtitles:
            # Use 'create_caption_image' from text logic (which we imported)
            # Assuming 'create_caption_image' draws text on transparent bg
            # We need to make sure we imported it or logic is here
            # We imported 'create_caption_image' at top.
            img = create_caption_image(text, video_width)
            # Fix positioning using bottom alignment
            txt = (
                ImageClip(img, transparent=True)
                .set_position(("center", video_height - 100)) # Bottom
                .set_start(start)
                .set_end(end)
            )
            subtitle_clips.append(txt)
        
        # Add to composition
        if subtitle_clips:
            final_clip = CompositeVideoClip(final_clip.clips + subtitle_clips, size=(video_width, video_height))

    # final_clip = final_clip.set_audio(audio) # NO AUDIO
    
    # Write File
    final_clip.write_videofile(
        output_path, fps=24, codec="libx264", audio=False, threads=4, logger=None
    )
    return True

# ==================================================================================
# UI: IMAGE SELECTION APP
# ==================================================================================

class ImageSelectionApp:
    def __init__(self, root, scenes_info):
        self.root = root
        self.root.title("Select Images for Scenes")
        self.root.geometry("1400x900")
        
        self.scenes_info = scenes_info # List of {id, candidates: [path1, path2...]}
        self.selections = {} # scene_id -> {path: BooleanVar}
        self.thumbnails = [] # Refs

        # Header
        tk.Label(root, text="Select 1 Image for Cutout/Effect OR Multiple for Collage", font=("Arial", 16, "bold")).pack(pady=10)
        
        btn_confirm = tk.Button(root, text="CONFIRM SELECTIONS", font=("Arial", 14, "bold"), bg="#4CAF50", fg="white",
                                command=self.on_confirm)
        btn_confirm.pack(pady=10)

        # Scrollable Area
        container = Frame(root)
        container.pack(fill="both", expand=True)
        canvas = Canvas(container)
        v_scroll = Scrollbar(container, orient="vertical", command=canvas.yview)
        
        scroll_frame = Frame(canvas)
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=v_scroll.set)
        
        v_scroll.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        
        # Mousewheel
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        
        # Populate
        thumb_h = 180
        
        for s_data in scenes_info:
            sid = s_data['id']
            paths = s_data['candidates']
            text_preview = s_data.get('text', '')
            
            row = Frame(scroll_frame, bd=1, relief="solid", padx=10, pady=10)
            row.pack(fill="x", padx=10, pady=5)
            
            # Header with Text
            header_frame = Frame(row)
            header_frame.pack(fill="x", pady=5)
            tk.Label(header_frame, text=f"Scene {sid}", font=("Arial", 12, "bold"), fg="#2196F3").pack(side="left", padx=10)
            tk.Label(header_frame, text=text_preview[:100]+"...", font=("Arial", 10, "italic"), fg="#555").pack(side="left")
            
            # Use StringVar for Single Selection
            selected_var = tk.StringVar(value="") 
            self.selections[sid] = selected_var
            
            # Default to first path if exists
            if paths:
                selected_var.set(paths[0])
            
            for p in paths:
                # Load thumb
                img = Image.open(p)
                ratio = img.width / img.height
                img_thumb = img.resize((int(thumb_h * ratio), thumb_h))
                tk_thumb = ImageTk.PhotoImage(img_thumb)
                self.thumbnails.append(tk_thumb)
                
                # Checkbox Frame -> Radio Frame
                chk_frame = Frame(row)
                chk_frame.pack(side="left", padx=15)
                
                # RadioButton
                rb = tk.Radiobutton(chk_frame, image=tk_thumb, variable=selected_var, value=p)
                rb.pack()
                tk.Label(chk_frame, text=os.path.basename(p)).pack()

    def on_confirm(self):
        self.final_selections = {} # scene_id -> list of selected paths
        
        for sid, var in self.selections.items():
            val = var.get()
            if val:
                self.final_selections[sid] = [val]
            else:
                 self.final_selections[sid] = []
            
        self.root.destroy()


# ==================================================================================
# UI: BATCH VERIFICATION APP (EFFECTS)
# ==================================================================================

class BatchVerificationApp:
    def __init__(self, root, scene_data_list):
        self.root = root
        self.root.title("Select Effects for Single Images")
        self.root.geometry("1400x900")
        
        self.scene_data_list = scene_data_list
        self.result_map = {} # scene_id -> choice_str
        
        # Header
        tk.Label(root, text="Select Video Effect", font=("Arial", 16, "bold")).pack(pady=10)
        
        btn_gen = tk.Button(root, text="GENERATE CLIPS", font=("Arial", 14, "bold"), bg="#2196F3", fg="white",
                            command=self.on_generate)
        btn_gen.pack(pady=10)
        
        # Scrollable Area
        container = Frame(root)
        container.pack(fill="both", expand=True)
        canvas = Canvas(container)
        v_scroll = Scrollbar(container, orient="vertical", command=canvas.yview)
        
        scroll_frame = Frame(canvas)
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=v_scroll.set)
        
        v_scroll.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        
        # Mousewheel
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        
        # Populate
        self.choices = {} # scene_id -> StringVar
        
        EFFECT_OPTIONS = [
            ("0", "Skip (Static)"),
            ("1", "Zoom Subject"),
            ("2", "Parallax"),
            ("3", "Floating"),
            ("4", "Zoom BG"),
            ("5", "Rotate"),
            ("6", "BW Reveal"),
            ("7", "Flash"),
            ("8", "Vignette"),
            ("9", "Spotlight"),
            ("10", "Tilt L/R"),
            ("11", "Move L/R"),
            ("12", "Fade In")
        ]
        
        for data in scene_data_list:
            sid = data['id']
            # PREVIEW GENERATION
            # show Original vs Foreground to check cutout quality
            orig_pil = data['original_pil']
            fg_pil = data['fg_pil']
            
            thumb_h = 180
            
            # 1. Original Thumb
            ratio_o = orig_pil.width / orig_pil.height
            thumb_w_o = int(thumb_h * ratio_o)
            orig_thumb = orig_pil.resize((thumb_w_o, thumb_h))
            tk_orig = ImageTk.PhotoImage(orig_thumb)
            
            # 2. Cutout Thumb (FG)
            # Create a checkerboard or dark bg for FG to see alpha
            fg_thumb = fg_pil.resize((thumb_w_o, thumb_h))
            # Composite on dark grey to see edges better
            bg_check = Image.new("RGB", fg_thumb.size, (50, 50, 50))
            bg_check.paste(fg_thumb, (0,0), fg_thumb)
            tk_fg = ImageTk.PhotoImage(bg_check)
            
            # Keep refs
            if not hasattr(self, 'thumbs'): self.thumbs = []
            self.thumbs.extend([tk_orig, tk_fg])
            
            row = Frame(scroll_frame, bd=1, relief="solid", padx=10, pady=10)
            row.pack(fill="x", padx=10, pady=5)
            
            # Images Container
            imgs_frame = Frame(row)
            imgs_frame.pack(side="left")
            
            # Show Original
            lbl_orig = tk.Label(imgs_frame, text="Original", font=("Arial", 8))
            lbl_orig.pack(anchor="w")
            tk.Label(imgs_frame, image=tk_orig).pack(anchor="w")
            
            # Show Cutout
            lbl_cut = tk.Label(imgs_frame, text="Cutout", font=("Arial", 8))
            lbl_cut.pack(anchor="w", pady=(5,0))
            tk.Label(imgs_frame, image=tk_fg).pack(anchor="w")
            
            # Controls
            ctrl_frame = Frame(row)
            ctrl_frame.pack(side="left", padx=20, fill="x", expand=True)
            
            tk.Label(ctrl_frame, text=f"Scene {sid}", font=("Arial", 14, "bold")).pack(anchor="w")
            tk.Label(ctrl_frame, text=data['audio_text'][:60]+"...", fg="#666").pack(anchor="w")
            
            # Radio Buttons
            choice_var = tk.StringVar(value="0") # Default Skip
            self.choices[sid] = choice_var
            
            # Grid layout for options
            opts_frame = Frame(ctrl_frame)
            opts_frame.pack(anchor="w", pady=5)
            
            r = 0
            c = 0
            for val, label in EFFECT_OPTIONS:
                rb = tk.Radiobutton(opts_frame, text=f"[{val}] {label}", variable=choice_var, value=val)
                rb.grid(row=r, column=c, sticky="w", padx=5)
                c += 1
                if c > 4: # Wrap
                    c = 0
                    r += 1

    def on_generate(self):
        # Collect results
        for sid, var in self.choices.items():
            self.result_map[sid] = var.get()
        self.root.destroy()


# ==================================================================================
# MAIN PROCESSOR
# ==================================================================================

def run_batch_processor(scenes_to_process):
    """
    1. Scan for multiple images.
    2. Show Selection App.
    3. If User selects > 1: Generate Collage Clip (Static).
    4. If User selects 1: Generate Cutout (Extract) -> Show BatchVerificationApp (Effects).
    """
    
    # 1. SCAN IMAGES
    print("\n[BATCH] Scanning for image candidates...")
    scene_candidates = [] # List of {id, candidates: []}
    
    # Map back from scenes_to_process which has 'image_path' (usually just one)
    # We want to find *all* for that scene_id
    
    base_images_dir = os.path.dirname(scenes_to_process[0]['image_path'])
    # Note: scenes_to_process might have passed a path like .../scene_1.png (legacy) 
    # or .../scene_1/img_1.png (new). We need the root images dir for the script.
    
    # If path ends with .png, dirname is the folder. 
    # If it was scene_1/img_1.png, dirname is scene_1. Parent is images/script_id.
    
    # Robust way: We know the structure is images/{script_id}/
    # Let's try to deduce the script_id dir.
    
    sample_path = scenes_to_process[0]['image_path']
    if "scene_" in os.path.basename(os.path.dirname(sample_path)):
         # We are in scenes/1/scene_1/img_1.png -> parent is script dir
         script_images_dir = os.path.dirname(os.path.dirname(sample_path))
    else:
         # We are in scenes/1/scene_1.png -> dirname is script dir
         script_images_dir = os.path.dirname(sample_path)

    for scene in scenes_to_process:
        sid = scene['id']
        candidates = []
        
        # 1. Check NEW nested structure: scene_{sid}/img_{1..3}.png
        scene_subfolder = os.path.join(script_images_dir, f"scene_{sid}")
        if os.path.exists(scene_subfolder):
            for i in range(1, 4):
                p = os.path.join(scene_subfolder, f"img_{i}.png")
                if os.path.exists(p):
                    candidates.append(p)
        
        # 2. Fallback: Check flat structure scene_{sid}_{i}.png or scene_{sid}.png
        if not candidates:
            for i in range(1, 4):
                p = os.path.join(script_images_dir, f"scene_{sid}_{i}.png")
                if os.path.exists(p):
                    candidates.append(p)
                    
        if not candidates:
            # Last resort: flat scene_{sid}.png
            p = os.path.join(script_images_dir, f"scene_{sid}.png")
            if os.path.exists(p):
                candidates.append(p)
                
                
        if candidates:
            # Pass 'text' for UI context
            text_preview = scene.get('audio_text', '')
            scene_candidates.append({"id": sid, "candidates": candidates, "text": text_preview})

    # 2. SELECT IMAGES
    print(f"[BATCH] Found candidates for {len(scene_candidates)} scenes. Launching Selection App...")
    
    root = tk.Tk()
    sel_app = ImageSelectionApp(root, scene_candidates)
    root.mainloop()
    
    if not hasattr(sel_app, 'final_selections'):
        print("[BATCH] Selection cancelled.")
        return

    selected_map = sel_app.final_selections # {id: [path1, path2...]}
    
    # 3. PROCESS SELECTIONS
    
    scenes_for_effect_ui = [] # To be sent to BatchVerificationApp (Single image)
    
    for scene in scenes_to_process:
        sid = scene['id']
        selected_paths = selected_map.get(sid, [])
        
        if not selected_paths:
            print(f"Skipping Scene {sid} (No images).")
            continue
            
        scene_audio = scene['audio_path']
        scene_out = scene['output_path']
        scene_text = scene.get('audio_text', '')
        
        # ALWAYS SINGLE processing now
        print(f"Scene {sid}: Image selected. preparing for Extraction...")
        
        # Use the selected path!
        chosen_img_path = selected_paths[0]
        
        # Extract
        fg, bg, orig = extract_layers(chosen_img_path)
        
        scenes_for_effect_ui.append({
            "id": sid,
            "fg_pil": fg,
            "bg_pil": bg,
            "original_pil": orig,
            "image_path": chosen_img_path,
            "audio_path": scene_audio,
            "output_path": scene_out,
            "audio_text": scene_text
        })

    # 4. EFFECT UI (For Single Images)
    if scenes_for_effect_ui:
        print(f"\n[BATCH] Launching Effect Verification for {len(scenes_for_effect_ui)} scenes...")
        root = tk.Tk()
        app = BatchVerificationApp(root, scenes_for_effect_ui)
        root.mainloop()
        
        if hasattr(app, 'result_map'):
             choices = app.result_map
             print("\n[BATCH] Rendering Effect Clips...")
             for data in scenes_for_effect_ui:
                 sid = data['id']
                 choice = choices.get(sid, "0")
                 
                 success = generate_single_clip_from_data(
                    data['fg_pil'], data['bg_pil'], choice, 
                    data['audio_path'], data['output_path'], data['audio_text']
                 )
                 if success: print(f"  -> Scene {sid} Effect Clip Generated.")

    print("\n[BATCH] All processing complete.")

