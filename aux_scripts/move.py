import os
import shutil

source_base = "outputs"          # where folders like 1/, 2/, 3/ exist
destination_base = "outputs/audios"  # new folder structure

# Create base destination folder
os.makedirs(destination_base, exist_ok=True)

for folder in os.listdir(source_base):
    source_folder_path = os.path.join(source_base, folder)

    # Only process numeric folders
    if not folder.isdigit() or not os.path.isdir(source_folder_path):
        continue

    # Source audios folder
    source_audio_dir = os.path.join(source_folder_path, "audios")

    if not os.path.exists(source_audio_dir):
        print(f"No audios folder in {source_audio_dir}")
        continue

    # Destination: output/audios/<id>/
    dest_audio_dir = os.path.join(destination_base, folder)
    os.makedirs(dest_audio_dir, exist_ok=True)

    # Move all files from outputs/<id>/audios/* to output/audios/<id>/*
    for file in os.listdir(source_audio_dir):
        src_file = os.path.join(source_audio_dir, file)
        dest_file = os.path.join(dest_audio_dir, file)

        shutil.move(src_file, dest_file)
        print(f"Moved {src_file} -> {dest_file}")
