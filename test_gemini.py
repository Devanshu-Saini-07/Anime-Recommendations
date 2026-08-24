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

response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents="Give me one anime recommendation in one sentence."
)

print(response.text)