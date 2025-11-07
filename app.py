import os
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech
from Backend.IoT import iot
from Backend.ImageGenration import GenerateImage
from Backend.Learning import run as LearningRecommender  # ✅ NEW IMPORT
from dotenv import dotenv_values
from asyncio import run
import eel  # GUI Framework

# Load environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Assistant")

# Initialize eel
eel.init("web")

# Display text on GUI and console
@eel.expose
def ShowTextToScreen(text):
    print(text)
    eel.updateScreenText(text)

# Supported functions (Automation / IoT / Media etc)
Functions = [
    'open', 'close', 'play', "system", "content",
    "google search", "youtube search", "iot",
    "LearningRecommender"   # ✅ ADDED
]

@eel.expose
def SetAssistantStatus(status):
    print(f"Assistant Status: {status}")
    eel.updateStatus(status)

def QueryModifier(query):
    return query.strip()

@eel.expose
def MainExecution():
    TaskExecution = False
    ImageExecution = False
    ImageGenerationQuery = ""

    Text = SpeechRecognition()  # Speech → text
    print(f"Recognized Text: {Text}")

    Query = ""

    if Text and "neuro" in Text.lower():  # Wake word
        Query = Text.lower().replace("neuro", "").strip()
        ShowTextToScreen(f"{Username} : {Query}")
        SetAssistantStatus("Thinking...")

        try:
            Decision = FirstLayerDMM(Query)
            print(f"Decision: {Decision}")

            # general & realtime detection
            G = any(i.startswith("general") for i in Decision)
            R = any(i.startswith("realtime") for i in Decision)

            MergedQuery = " and ".join(
                [" ".join(i.split()[1:]) for i in Decision if (i.startswith("general") or i.startswith("realtime"))]
            )

            # ✅ ✅ ✅ LEARNING RECOMMENDER
            for d in Decision:
                if d.startswith("LearningRecommender"):
                    SetAssistantStatus("Preparing learning recommendations...")

                    text, payload = LearningRecommender(Query)

                    ScreenFeedback = f"{Assistantname}: {text}"
                    SpokenFeedback = "Here are some learning resources I recommend."

                    ShowTextToScreen(ScreenFeedback)
                    TextToSpeech(SpokenFeedback)

                    # Optionally print recommendations in console
                    if payload and "recommendations" in payload:
                        for r in payload["recommendations"]:
                            print(f"- {r['title']} ({r['type']})")

                    SetAssistantStatus("Answering...")
                    return True

            # ✅ IMAGE GENERATION
            for d in Decision:
                if d.startswith("generate image"):
                    ImageGenerationQuery = d.replace("generate image ", "")
                    ImageExecution = True

            if ImageExecution:
                try:
                    GenerateImage(ImageGenerationQuery)
                    ScreenFeedback = f"{Assistantname}: Image generated successfully!"
                    ShowTextToScreen(ScreenFeedback)
                    TextToSpeech("The image has been generated.")
                except Exception as e:
                    ShowTextToScreen(f"{Assistantname}: Error generating image.")
                    TextToSpeech("Sorry, an error occurred.")

            # ✅ AUTOMATION (OPEN / CLOSE / PLAY / SYSTEM / etc)
            for d in Decision:
                if not TaskExecution and any(d.startswith(func) for func in Functions) and not d.startswith("LearningRecommender"):
                    run(Automation(Decision))
                    TaskExecution = True
                    ShowTextToScreen(f"{Assistantname}: Task executed successfully.")
                    TextToSpeech("Task executed successfully.")
                    return True

            # ✅ REALTIME SEARCH
            if R:
                SetAssistantStatus("Searching...")
                Answer = RealtimeSearchEngine(QueryModifier(MergedQuery))
                ShowTextToScreen(f"{Assistantname}: {Answer}")
                TextToSpeech(Answer)
                return True

            # ✅ GENERAL CHATBOT
            if G:
                SetAssistantStatus("Thinking...")
                Answer = ChatBot(QueryModifier(Query))
                ShowTextToScreen(f"{Assistantname}: {Answer}")
                TextToSpeech(Answer)
                return True

            # ✅ EXIT
            for d in Decision:
                if d.startswith("exit"):
                    TextToSpeech("Okay, goodbye.")
                    os._exit(1)

            # ✅ IOT
            for d in Decision:
                if d.startswith("iot"):
                    SetAssistantStatus("Switching devices...")
                    cmd = d.replace("iot ", "")
                    Answer = iot(cmd)
                    ShowTextToScreen(f"{Assistantname}: {Answer}")
                    TextToSpeech(Answer)
                    return True

        except Exception as e:
            print("Error:", e)
            ShowTextToScreen(f"{Assistantname}: Something went wrong.")
            TextToSpeech("Sorry, something went wrong.")

    else:
        print("Skipping: 'neuro' not detected")
        return

if __name__ == "__main__":
    eel.start("index.html", size=(1024, 768), mode="chrome")

    while True:
        MainExecution()
