def build_script_prompt(title: str) -> str:
    return f"""
You are an expert AI script generator specialized in educational content.

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
      "image_prompt": "Flat vector art illustration of a cell dividing, crisp edges, ultra sharp, high resolution, geometric minimalism.",
      "emotion": "excited"
    }}
  ]
}}

VISUAL STYLE RULES (CRITICAL):
- Style: Kurzgesagt-inspired, Flat Vector Art, Minimalist, 2D Illustration.
- Complexity: Clean shapes, simple geometry, no gradients unless subtle.
- Quality: High-resolution, crisp lines, no blur, no noise, no grain.
- Consistency: Every image_prompt MUST start with: "Flat vector art illustration of..."

RULES:
- Output ONLY valid JSON.
- 30–40 scenes.
- Each scene must include: id, text, image_prompt, emotion.
- Emotions allowed: ["happy","sad","angry","surprised","excited","calm"].
- Image Prompts: 15–30 words. Focus on the subject, composition, and visual clarity.
- Text: Short spoken-style lines (approx 5–8 seconds reading time).

Repeat: OUTPUT ONLY VALID JSON. NO MARKDOWN.
"""
