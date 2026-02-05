def build_educational_script_prompt(title: str) -> str:
    return f"""
You are an expert educational storyteller and psychology researcher.
Your task is to write a deep, engaging, and clear educational script on the topic: "{title}".

GUIDELINES:
1.  **Structure**: Start with a strong hook, then explain the concept clearly, provide examples/insights, and end with a resolution/takeaway.
2.  **Tone**: Calm, human, professional, curious, and intelligent. NOT motivational hype.
3.  **Length**: Comprehensive enough to cover the topic well (approx. 30-40 phrases/ideas).
4.  **Format**: Just write the raw script text. Paragraphs are fine.

GOAL:
Teach the user about "{title}" in a way that feels like a high-quality documentary narration.
"""


def build_scene_generation_prompt(educational_script: str) -> str:
    return f"""
You are an expert AI Screenwriter and Director.
I will provide you with an educational script. Your job is to convert it into a structured JSON format for video generation.

INPUT SCRIPT:
"{educational_script}"

INSTRUCTIONS:
1.  **Break Down**: Split the script into small, spoken-style scenes (1-3 sentences max per scene).
    -   Each scene must be a logical "beat" of the story.
    -   Do NOT cram too much text into one scene.
2.  **Visuals**: For EACH scene, generate EXACTLY 3 DISTINCT image prompts.
    -   These 3 prompts must describe completely different visuals that represent the SAME idea.
    -   This gives us options to choose the best one later.

STRICT JSON OUTPUT FORMAT:
{{
  "title": "Derived Title",
  "description": "Short description",
  "scenes": [
    {{
      "id": 1,
      "text": "First chunk of narration...",
      "image_prompts": [
        "cartoonish image of a [Concept A]...",
        "cartoonish image of a [Concept B]...",
        "cartoonish image of a [Concept C]..."
      ],
      "audio_delay": 0.5,
      "emotion": "calm"
    }}
  ]
}}

IMAGE PROMPT RULES (CRITICAL):
-   **Quantity**: EXCEPTLY 3 prompts per scene.
-   **Variety**: The 3 prompts must look DIFFERENT (e.g., one literal, one metaphorical, one abstract object).
-   **Style**: "cartoonish image of..." (ALWAYS start with this).
-   **Content**: Simple objects, clear composition, minimal detail. No complex scenes.
-   **Constraints**: No text in images, no faces, clean cartoon style.

SCENE RULES:
-   **Text**: Keep it spoken and natural.
-   **Sequential**: ids must go 1, 2, 3...
-   **Audio Delay**: explicit pause after this scene in seconds (0.5 to 2.0).

OUTPUT ONLY THE VALID JSON OBJECT. NO MARKDOWN. NO EXTRA TEXT.
"""
