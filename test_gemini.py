from dotenv import load_dotenv
import os
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

response = client.models.generate_content(
    model="models/gemini-3.6-flash",
    contents="안녕! 한 줄로 자기소개해줘."
)

print(response.text)