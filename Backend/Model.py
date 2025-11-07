# Backend/Model.py
import json
from dotenv import dotenv_values
import google.generativeai as genai

env = dotenv_values(".env")
GEMINI_API_KEY = env.get("GEMINI_API_KEY")

# ✅ Configure Gemini correctly (new API)
genai.configure(api_key=GEMINI_API_KEY)

# Valid function types
funcs = [
    "exit", "general", "realtime", "open", "close", "play",
    "generate image", "system", "content", "google search",
    "youtube search", "reminder", "iot", "LearningRecommender"
]

preamble = """
You are a Decision-Making Model. Do NOT answer questions directly.

You must label the user's query into one of the functions:

- LearningRecommender (topic)
- general (query)
- realtime (query)
- open (app)
- close (app)
- play (song)
- generate image (prompt)
- google search (query)
- youtube search (query)
- content (topic)
- reminder (datetime)
- system (command)
- iot (device action)
- exit

*** ONLY return the label. Do not explain. No full sentences. ***
Examples:
"how do I learn python?" → LearningRecommender python
"who is Albert Einstein?" → general who is Albert Einstein?
"open youtube" → open youtube
"turn on the lights" → iot light on
"""

ChatHistory = [
    {"role": "user", "content": "recommend resources for python"},
    {"role": "assistant", "content": "LearningRecommender python"},
    {"role": "user", "content": "who is apj abdul kalam"},
    {"role": "assistant", "content": "general who is apj abdul kalam"},
    {"role": "user", "content": "open chrome"},
    {"role": "assistant", "content": "open chrome"}
]

def FirstLayerDMM(prompt: str = "test"):
    try:
        model = genai.GenerativeModel("gemini-2.5-pro")

        # Build classification prompt
        full_prompt = (
            preamble
            + "\nHistory:\n"
            + "\n".join([f"User: {m['content']}" if m["role"] == "user" else f"Assistant: {m['content']}" for m in ChatHistory])
            + f"\nUser: {prompt}\nAssistant:"
        )

        # Generate classification
        response = model.generate_content(full_prompt)
        text = response.text.strip().lower()

        # Multiple commands separated by comma
        parts = [t.strip() for t in text.split(",")]

        cleaned = []
        for p in parts:
            if any(p.startswith(k) for k in funcs):
                cleaned.append(p)

        # Default fallback
        if not cleaned:
            cleaned = [f"general {prompt}"]

        return cleaned

    except Exception as e:
        print("Decision error:", e)
        return [f"general {prompt}"]

if __name__ == "__main__":
    while True:
        q = input("Query: ")
        print(FirstLayerDMM(q))

