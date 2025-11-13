from run_pipeline.generate_images import generate_images
from run_pipeline.generate_script import generate_Script_Gemini
from run_pipeline.generate_audios import generate_audios
from scripts.tts_env import activate_ttsenv, deactivate_ttsenv
from run_pipeline.generate_all_clips import generate_all_clips
from run_pipeline.generate_final_video import generate_final_video


TITLE_ID = "2"
TITLE_NAME = "Why is the sky blue?"

# === generate the script with text and image prompt ===
filepath_to_script = generate_Script_Gemini(TITLE_NAME,TITLE_ID)
# filepath_to_script ---> outputs\1\script.json

# filepath_to_script = "outputs/2/script.json"

# print(f"Script generated at: {filepath_to_script}")
# activate ttsenv
# env_process = activate_ttsenv()


#2 generate_audios(filepath_to_script)
generate_audios(filepath_to_script)

#3 generate_images from the script prompts
generate_images(filepath_to_script)

# deactivate_ttsenv(env_process)

#merge image and audio to multiple video
generate_all_clips(filepath_to_script)


# merge all clips to a single video
final_path = generate_final_video(filepath_to_script)