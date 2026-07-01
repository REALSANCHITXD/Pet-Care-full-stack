from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), "secret.env")
load_dotenv(dotenv_path=env_path)

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_PROMPT = """
You are Dr. Paws, an expert AI veterinary assistant for a pet care platform.
Your job is to help pet owners with questions about their pets' health, diet, 
behavior, and general care.

Rules:
- Always be warm, friendly, and empathetic.
- If symptoms sound serious or life-threatening, always recommend the user 
  visit a real veterinarian immediately.
- Keep answers concise and easy to understand (avoid heavy medical jargon).
- You can help with Dogs, Cats, Birds, Fish, Rabbits, and other common pets.
- Never diagnose a pet with certainty — always phrase it as a possibility.
- If the user asks something unrelated to pets, politely redirect them.
"""

def get_ai_response(chat_history: list, new_message: str) -> str:
    contents = []
    for msg in chat_history:
        role = "user" if msg['sender'] == 'user' else "model"
        contents.append(types.Content(role=role, parts=[types.Part(text=msg['message'])]))
    
    contents.append(types.Content(role="user", parts=[types.Part(text=new_message)]))

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
        contents=contents
    )
    return response.text
