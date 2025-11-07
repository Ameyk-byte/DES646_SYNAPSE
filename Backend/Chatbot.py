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

# ✅ Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Ensure Data folder exists
if not os.path.exists("Data"):
    os.makedirs("Data")

CHAT_LOG_PATH = "Data/ChatLog.json"

# System instructions + real-time info
def RealtimeInformation():
    now = datetime.datetime.now()
    return (
        f"Use this real-time info only if needed.\n"
        f"Day: {now.strftime('%A')}\n"
        f"Date: {now.strftime('%d')}\n"
        f"Month: {now.strftime('%B')}\n"
        f"Year: {now.strftime('%Y')}\n"
        f"Time: {now.strftime('%H')} hours : {now.strftime('%M')} minutes : {now.strftime('%S')} seconds.\n"
    )

SYSTEM_MESSAGE = (
    f"You are {Assistantname}, a helpful and accurate AI assistant.\n"
    f"User is {Username}.\n"
    "*** Follow these rules strictly: ***\n"
    "- Reply only in English.\n"
    "- Do not say the time/date unless asked.\n"
    "- Do not talk too much, keep it concise.\n"
    "- Never mention training data.\n"
)

# Load chat history if exists
def load_chat():
    if os.path.exists(CHAT_LOG_PATH):
        try:
            with open(CHAT_LOG_PATH, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def save_chat(messages):
    with open(CHAT_LOG_PATH, "w") as f:
        json.dump(messages, f, indent=4)

def clean_answer(text: str) -> str:
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    return "\n".join(lines)

def ChatBot(Query: str) -> str:
    """Generate a response using Gemini with chat history + system messages."""
    messages = load_chat()

    # Build prompt
    history_text = ""
    for m in messages[-10:]:
        role = m["role"]
        content = m["content"]
        history_text += f"{role.upper()}: {content}\n"

    full_prompt = (
        f"{SYSTEM_MESSAGE}\n"
        f"{RealtimeInformation()}\n\n"
        f"{history_text}"
        f"USER: {Query}\n"
        f"ASSISTANT:"
    )

    try:
        model = genai.GenerativeModel("gemini-2.5-pro")

        response = model.generate_content(
            full_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                top_p=1,
                max_output_tokens=512,
            )
        )

        # ✅ Safely get AI answer
        if hasattr(response, "text") and response.text:
            Answer = response.text.strip()
        elif response.candidates and response.candidates[0].content.parts:
            Answer = response.candidates[0].content.parts[0].text
        else:
            Answer = "I'm unable to generate a complete answer right now."

        Answer = clean_answer(Answer)

        # Save to log
        messages.append({"role": "user", "content": Query})
        messages.append({"role": "assistant", "content": Answer})
        save_chat(messages)

        return Answer

    except Exception as e:
        print("Chatbot error:", e)
        return "Sorry, something went wrong while generating a response."


if __name__ == "__main__":
    while True:
        user_input = input("You: ")
        print("Neuro:", ChatBot(user_input))
