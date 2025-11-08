# Backend/Chatbot.py
import os
import json
import datetime
from dotenv import dotenv_values
import google.generativeai as genai

# Load .env
env = dotenv_values(".env")
Username = env.get("Username", "User")
Assistantname = env.get("Assistantname", "Neuro")
GEMINI_API_KEY = env.get("GEMINI_API_KEY")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

if not os.path.exists("Data"):
    os.makedirs("Data")

CHAT_LOG_PATH = "Data/ChatLog.json"

def RealtimeInformation():
    now = datetime.datetime.now()
    return (
        f"Use this only when needed.\n"
        f"Day: {now.strftime('%A')}, "
        f"Date: {now.strftime('%d')} {now.strftime('%B')} {now.strftime('%Y')}, "
        f"Time: {now.strftime('%H:%M:%S')}.\n"
    )

SYSTEM_MESSAGE = (
    f"You are {Assistantname}, a helpful AI assistant.\n"
    f"User is {Username}.\n"
    "Rules:\n"
    "- Reply only in English.\n"
    "- Keep answers short.\n"
    "- Do not mention time unless asked.\n"
    "- Do not mention training data.\n"
)

def load_chat():
    try:
        if os.path.exists(CHAT_LOG_PATH):
            with open(CHAT_LOG_PATH, "r") as f:
                return json.load(f)
    except:
        pass
    return []

def save_chat(messages):
    with open(CHAT_LOG_PATH, "w") as f:
        json.dump(messages, f, indent=4)

def safe_extract(response):
    """Safely extract text even when response.text is missing."""
    try:
        # Preferred output
        if hasattr(response, "text") and response.text:
            return response.text.strip()

        # Fallback
        if response.candidates:
            cand = response.candidates[0]
            if cand.content.parts:
                return cand.content.parts[0].text

        # If still nothing:
        return None
    except:
        return None

def ChatBot(Query: str) -> str:
    messages = load_chat()

    # Use last 8 messages for context
    history = ""
    for m in messages[-8:]:
        history += f"{m['role'].upper()}: {m['content']}\n"

    full_prompt = (
        f"{SYSTEM_MESSAGE}\n"
        f"{RealtimeInformation()}\n\n"
        f"{history}\n"
        f"USER: {Query}\n"
        f"ASSISTANT:"
    )

    try:
        model = genai.GenerativeModel("gemini-2.5-pro")

        response = model.generate_content(
            full_prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=250,
                temperature=0.6,
                top_p=1
            )
        )

        Answer = safe_extract(response)

        # ✅ If Gemini sends NO valid content, retry with safer prompt
        if Answer is None or Answer.strip() == "":
            safe_prompt = f"{SYSTEM_MESSAGE}\nAnswer briefly: {Query}"
            response2 = model.generate_content(safe_prompt)
            Answer = safe_extract(response2)

        # ✅ If still empty, final fallback
        if Answer is None or Answer.strip() == "":
            Answer = "I'm unable to generate a response right now."

        # Save history
        messages.append({"role": "user", "content": Query})
        messages.append({"role": "assistant", "content": Answer})
        save_chat(messages)

        return Answer

    except Exception as e:
        print("Chatbot error:", e)
        return "Sorry, something went wrong while generating a response."
