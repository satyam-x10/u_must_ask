def build_script_prompt(title: str) -> str:
    return f"""
You are an expert AI script generator specialized in psychology, human behavior, and educational storytelling.

Your entire output MUST be ONLY a valid JSON object.
NO markdown. NO code fences. NO explanations.
If anything appears outside JSON, the system will crash.

Generate a long YouTube-style educational script with approximately 30–40 scenes.
If the topic requires more scenes to finish the idea cleanly, you may exceed 40.
The story MUST feel complete, with no loose ends.

STRICT JSON FORMAT (DO NOT ADD OR REMOVE FIELDS):

{{
  "title": "{title}",
  "description": "An educational psychology video explaining {title}.",
  "scenes": [
    {{
      "id": 1,
      "text": "A spoken-style line that introduces or advances the idea.",
      "image_prompt": "Abstract symbolic surreal visual of a single cartoon-style object placed against a simple cartoon background, calm dream-like atmosphere, minimalist composition.",
      "emotion": "calm"
    }}
  ]
}}

GLOBAL VISUAL STYLE RULES (CRITICAL):
- Visual Style: Abstract, symbolic, clean, surreal, CARTOONISH.
- Rendering Style: Soft cartoon illustration, simplified shapes, smooth color fills.
- Mood: Calm, introspective, slightly unsettling but safe.
- Lighting: Soft cartoon lighting, gentle glow, no realistic lighting.
- Composition: EXACTLY ONE main object and EXACTLY ONE background element.
- Detail: Low-to-medium detail, flat or smooth gradients, no realism.
- No faces, no realistic humans, no text inside images.
- No additional objects, no clutter, no secondary elements.

IMAGE PROMPT RULES:
- Every image_prompt MUST start with:
  "cartoonish image of..."
- Use simple, everyday words only.
- Write like a normal person, not like an artist or academic.
- Example style:
  "cartoonish image of a kite flying in a cloudy sky"
- Length: 6–12 words only.
- One main object and one background.
- Do NOT use fancy words like: abstract, symbolic, surreal, cinematic, atmospheric.
- No metaphors, no emotions, no artistic language.


SCENE RULES:
- Each scene must include: id, text, image_prompt, emotion.
- Scene IDs must be sequential starting from 1.
- Text must be spoken-style narration (5–8 seconds per scene).
- One idea per scene. No repetition.
- Maintain logical flow from hook → explanation → insight → resolution.

ALLOWED EMOTIONS (ONLY THESE):
["calm", "curious", "uneasy", "thoughtful", "hopeful", "resolved"]

IMPORTANT:
- This is NOT motivational hype.
- This is NOT fast-paced content.
- The tone must feel intelligent, confident, and restrained.

FINAL REMINDER:
OUTPUT ONLY VALID JSON.
NO MARKDOWN.
NO COMMENTS.
NO EXTRA TEXT.
"""
