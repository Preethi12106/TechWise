import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

# Load .env from the TechWise root folder
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY not found")

client = OpenAI(api_key=api_key)

response = client.responses.create(
    model="gpt-5.6-luna",
    input="Explain what a software engineering decision is in one simple sentence."
)

print(response.output_text)