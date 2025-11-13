def build_script_prompt(title: str) -> str:
    """
    Builds a detailed prompt for Gemini to generate a YouTube-style,
    emotionally engaging and long-format video script (~3 minutes),
    including scene text, AI image prompts, and an emotion tag.
    """

    template = f"""
You are an expert AI storyteller and YouTube scriptwriter.
Your goal is to create a long-form, high-retention educational or storytelling video script for the given title.

Generate a **JSON object** that includes:
1. Engaging spoken dialogue for each scene.
2. A detailed visual prompt for AI image generation.
3. An **emotion tag** for each scene using ONLY one of:
   ["happy", "sad", "angry", "surprised", "excited", "calm"]

Follow this exact structure:

{{
  "title": "{title}",
  "scenes": [
    {{
      "id": 1,
      "text": "Opening hook that grabs instant attention, creating curiosity or emotional impact. Speak like a top YouTuber.",
      "prompt": "A visually striking or symbolic image that captures the essence of the opening moment.",
      "emotion": "excited"
    }},
    {{
      "id": 2,
      "text": "Build intrigue by setting up the premise — why this topic matters, what's mysterious or fascinating about it.",
      "prompt": "A relevant cinematic or realistic image to represent this setup moment.",
      "emotion": "surprised"
    }},
    ...
  ]
}}

### RULES:
- Output **valid JSON only** — no explanations, markdown, or comments.
- Use **6–8 words per sentence**, natural spoken tone, short sentences, emotional rhythm.
- Make the **full script long enough for a 3-minute video** (≈ 30–40 scenes).
- Write like a **charismatic YouTuber** — curious, confident, relatable, emotionally expressive.
- Maintain a strong **hook → curiosity → explanation → emotional closure** flow.
- Each “text” must sound like spoken monologue, not formal narration.
- Each “prompt” must be a **detailed, vivid description** (10–25 words).
- ALWAYS include an **emotion** field for every scene using ONLY:
  happy, sad, angry, surprised, excited, calm.
- No camera directions, timestamps, or markdown.

Title: "{title}"
"""
    return template.strip()
