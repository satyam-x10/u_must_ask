def build_script_prompt(title: str) -> str:
    return f"""
You are an expert AI script generator.

Your entire output MUST be ONLY a JSON object.
No markdown. No code fences. No explanations. No text before or after JSON.
If you include anything else, the system will crash.

Generate a long YouTube-style educational script with 30–40 scenes.

STRICT JSON FORMAT (DO NOT ADD ANYTHING OUTSIDE THIS):

{{
  "title": "{title}",
  "scenes": [
    {{
      "id": 1,
      "text": "Opening hook that grabs attention.",
      "prompt": "Beautiful cinematic symbolic opening image.",
      "emotion": "excited"
    }}
  ]
}}

RULES:
- Output ONLY valid JSON.
- 30–40 scenes.
- Each scene must include: id, text, prompt, emotion.
- Emotions allowed: ["happy","sad","angry","surprised","excited","calm"].
- Write in spoken YouTuber tone.
- Prompts: 10–25 descriptive words.
- Text: short natural spoken lines.

Repeat: OUTPUT ONLY VALID JSON. NO MARKDOWN.
"""
