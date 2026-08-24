import json
import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError("GEMINI_API_KEY is missing")

client = genai.Client(
    api_key=api_key,
    http_options={
        "timeout": 30000
    }
)


def get_recommendations(preferences, watch_history, candidates):
    prompt = f"""
You are an anime recommendation engine.

User's preferred genres:
{json.dumps(preferences)}

Anime already in the user's watch history:
{json.dumps(watch_history)}

Available anime candidates:
{json.dumps(candidates)}

Recommend up to 6 anime from ONLY the available candidates.

STRICT RULES:
1. Never recommend an anime already present in the watch history.
2. Recommend ONLY anime from the available candidates.
3. Prioritize the user's preferred genres.
4. Do not invent anime titles.
5. Return ONLY valid JSON.
6. Each recommendation must contain:
   - title
   - reason
   - genres
   - match_score

Return this exact JSON format:

[
  {{
    "title": "Anime Title",
    "reason": "Why this matches the user's taste",
    "genres": ["Action", "Fantasy"],
    "match_score": 92
  }}
]
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    text = response.text.strip()

    # Remove markdown code fences if Gemini adds them
    if text.startswith("```"):
        text = text.replace("```json", "", 1)
        text = text.replace("```", "", 1).strip()

    try:
        recommendations = json.loads(text)
    except json.JSONDecodeError:
        return []

    if not isinstance(recommendations, list):
        return []

    return recommendations