import os
os.environ["QT_LOGGING_RULES"] = "qt.qpa.*=false"
from dotenv import dotenv_values
from asyncio import run

from pynput import keyboard  # macOS-friendly hotkey

from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech
from Backend.IoT import iot
from Backend.ImageGenration import GenerateImage
from Backend.Learning import run as LearningRecommender

# Load .env
env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Neuro")

def ShowTextToScreen(text):
    print(text)

Functions = [
    'open','close','play',"system","content",
    "google search","youtube search","iot","LearningRecommender"
]

def SetAssistantStatus(status):
    print(f"Assistant Status: {status}")

def QueryModifier(query):
    return query.strip()

def ProcessQuery(Query):
    ShowTextToScreen(f"{Username} : {Query}")
    SetAssistantStatus("Processing...")
    try:
        Decision = FirstLayerDMM(Query)
        print(f"Decision: {Decision}")

        # Learning recommender
        for d in Decision:
            if d.startswith("LearningRecommender"):
                SetAssistantStatus("Preparing learning recommendations...")
                text, payload = LearningRecommender(Query)
                ShowTextToScreen(f"{Assistantname}: {text}")
                TextToSpeech("Here are personalized learning resources.")
                return

        # Image generation
        for d in Decision:
            if d.startswith("generate image"):
                prompt = d.replace("generate image ", "")
                GenerateImage(prompt)
                ShowTextToScreen(f"{Assistantname}: Image generated.")
                TextToSpeech("Image generated successfully.")
                return

        # IoT
        for d in Decision:
            if d.startswith("iot"):
                SetAssistantStatus("Switching...")
                cmd = d.replace("iot ", "")
                ans = iot(cmd)
                ShowTextToScreen(f"{Assistantname}: {ans}")
                TextToSpeech(ans)
                return

        # Automation
        for d in Decision:
            if any(d.startswith(func) for func in Functions) and not d.startswith("LearningRecommender"):
                run(Automation(Decision))
                ShowTextToScreen(f"{Assistantname}: Task executed.")
                TextToSpeech("Task executed successfully.")
                return

        # Realtime
        if any(d.startswith("realtime") for d in Decision):
            SetAssistantStatus("Searching...")
            Answer = RealtimeSearchEngine(QueryModifier(Query))
            ShowTextToScreen(f"{Assistantname}: {Answer}")
            TextToSpeech(Answer)
            return

        # General
        if any(d.startswith("general") for d in Decision):
            SetAssistantStatus("Thinking...")
            Answer = ChatBot(QueryModifier(Query))
            ShowTextToScreen(f"{Assistantname}: {Answer}")
            TextToSpeech(Answer)
            return

        # Exit
        if any(d.startswith("exit") for d in Decision):
            TextToSpeech("Goodbye!")
            os._exit(0)

    except Exception as e:
        print("Error:", e)
        ShowTextToScreen(f"{Assistantname}: Something went wrong.")
        TextToSpeech("Something went wrong.")

def VoiceCapture():
    text = SpeechRecognition()
    if text:
        text = text.lower()
        if "neuro" in text:
            Query = text.replace("neuro", "").strip()
            ProcessQuery(Query)
        else:
            print("Wake word not detected, ignoring...")

# ---- Hotkey using pynput: SHIFT + SPACE ----
print("✅ Neuro is running.")
print("👉 Press SHIFT + SPACE to talk.")

combo = {keyboard.Key.shift, keyboard.Key.space}
current = set()

def on_press(key):
    try:
        if key in combo:
            current.add(key)
        if combo.issubset(current):
            VoiceCapture()
    except Exception:
        pass

def on_release(key):
    try:
        if key in current:
            current.remove(key)
    except Exception:
        pass

with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
