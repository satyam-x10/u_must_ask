import os
import random
from bark import SAMPLE_RATE, generate_audio
from scipy.io.wavfile import write as write_wav

# Create output folder
os.makedirs("outputs", exist_ok=True)

VOICE_SETTINGS = {
    "dev": {"preset": "v2/en_speaker_1"},
    "ai_researcher": {"preset": "v2/en_speaker_5"},
}

CHARACTERS = ["dev", "ai_researcher"]

text = (
    "Scientists can map our brains, track our thoughts, and analyze every move we make — "
    "yet that strange internal knowing, that powerful whisper of intuition, is still the one "
    "human ability they can’t fully explain."
)

for i, person in enumerate(CHARACTERS):
    preset = VOICE_SETTINGS[person]["preset"]

    print(f"Generating for {person} ({preset}) → {text}")

    try:
        audio_array = generate_audio(
            text,
            history_prompt=preset
        )

        filename = f"outputs/{i:02d}_{person}.wav"
        write_wav(filename, SAMPLE_RATE, audio_array)

    except Exception as e:
        print(f"Error generating for {person}: {e}")

print("\nAll Bark audio files saved in 'outputs/'")
