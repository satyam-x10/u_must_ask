import os
import random
from bark import SAMPLE_RATE, generate_audio
from scipy.io.wavfile import write as write_wav

# Create output folder
os.makedirs("outputs", exist_ok=True)

# Random lines in explanatory tone
RANDOM_LINES = [
    "Let me explain this in a simple way. When we talk about artificial intelligence, we are referring to systems that can learn, reason, and make decisions. Essentially, AI tries to mimic human thinking, but does it using algorithms and data.",
    "Here is an easy explanation. Imagine you have a system that studies thousands of examples. Over time, it begins to understand patterns. This is the foundation of how modern machine learning works.",
    "To put it simply, technology evolves by learning from information. The more data it processes, the smarter it becomes. This is why AI today can solve complex problems with surprising accuracy.",
]

# Best Bark voices for explanation
VOICE_SETTINGS = {
    "dev": {"preset": "v2/en_speaker_1"},           # best clarity
    "ai_researcher": {"preset": "v2/en_speaker_5"}, # deep & professional
}

# Characters to generate
CHARACTERS = ["dev", "ai_researcher"]

for i in range(1, 6):   # generate 5 random clips
    for person in CHARACTERS:
        text = random.choice(RANDOM_LINES)

        

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
