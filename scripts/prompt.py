def build_script_prompt(title: str) -> str:
    """
    Builds a detailed prompt for Gemini to generate a YouTube-style, 
    emotionally engaging and long-format video script (~3 minutes),
    including scene text and AI image prompts.
    """

    template = f"""
You are an expert AI storyteller and YouTube scriptwriter.  
Your goal is to create a long-form, high-retention educational or storytelling video script for the given title.

Generate a **JSON object** that includes both:
1. Engaging, natural spoken dialogue for each scene.
2. A detailed visual prompt (for AI image generation) matching that scene.

Follow this exact structure and style:

{{
  "title": "{title}",
  "scenes": [
    {{
      "id": 1,
      "text": "Opening hook that grabs instant attention, creating curiosity or emotional impact. Speak like a top YouTuber, not a narrator.",
      "prompt": "A visually striking or symbolic image that captures the essence of the opening moment."
    }},
    {{
      "id": 2,
      "text": "Build intrigue by setting up the premise — why this topic matters, what's mysterious or fascinating about it.",
      "prompt": "A relevant cinematic or realistic image to represent this setup moment."
    }},
    ...
  ]
}}

### RULES:
- Output **valid JSON only** — no explanations, markdown, or comments.
- Use **6–8 words per sentence**, natural spoken tone, short sentences, emotional rhythm.
- Make the **full script long enough for a 3-minute video** (≈ 30–40 scenes if each lasts ~5 seconds).
- Write like a **YouTuber with charisma** — curious, confident, and relatable.
- Maintain a strong **hook → curiosity → explanation → emotional closure** flow.
- Avoid robotic phrasing, filler lines, or generic teaching tone.
- Each “text” must sound like part of a compelling narrative or spoken monologue.
- Each “prompt” should be a **detailed, vivid description** (10–25 words) for an AI image generator.
- Style for “prompt”: cinematic, ultra-realistic, or minimalist vector — whichever fits the scene’s emotion.
- Do **not** include camera directions, timestamps, or markdown.

Title: "{title}"
"""
    return template.strip()
