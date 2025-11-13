# test_gemini.py
"""
A minimal, production-ready Gemini 2.5 Flash test script.

Features:
- Loads API key securely from .env
- Handles missing/invalid keys gracefully
- Clean error handling
- Supports interactive prompt input for testing
"""

import os
from google import genai
from dotenv import load_dotenv

# === Load environment variables ===
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise EnvironmentError(
        "❌ Missing GOOGLE_API_KEY in .env file.\n"
        "Get one from https://aistudio.google.com/app/apikey"
    )

# === Initialize Gemini client ===
client = genai.Client(api_key=API_KEY)
model = "gemini-2.5-flash"

def generate_script(prompt: str) -> str:
    """
    Sends a text prompt to Gemini and returns the plain text response.
    """
    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt.strip()
        )
        return response.text.strip() if response.text else "⚠️ No response text received."
    except Exception as e:
        return f"❌ Gemini API Error: {e}"

