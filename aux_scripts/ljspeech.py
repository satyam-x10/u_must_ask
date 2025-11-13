import json
import os
from TTS.api import TTS

# Load single-speaker model (LJSpeech)
tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=True, gpu=False)

# Load dialogue script
with open("script.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Output directory
os.makedirs("outputs", exist_ok=True)

# Voice configuration
# Since this model has only one voice, we'll emulate differences by changing speed and pitch
VOICE_SETTINGS = {
    "dev": {"speed": 1.05, "speaker_wav": None},
    "ai_researcher": {"speed": 0.95, "speaker_wav": None},
}

# Loop and generate
for i, line in enumerate(data, start=1):
    person = line["person_id"]
    statement = line["statement"]
    filename = f"outputs/{i:02d}_{person}.wav"

    print(f"Generating voice for {person}: {statement}")

    settings = VOICE_SETTINGS.get(person, {})
    speed = settings.get("speed", 1.0)
    speaker_wav = settings.get("speaker_wav", None)

    try:
        # Use optional parameters for speed and reference voice if available
        tts.tts_to_file(
            text=statement,
            file_path=filename,
            speaker_wav=speaker_wav,
            speed=speed
        )
    except Exception as e:
        print(f"Error generating for {person}: {e}")

print("\n All audio files generated in the 'outputs' folder.")
