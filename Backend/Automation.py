import webbrowser
import subprocess
import asyncio
import paho.mqtt.client as mqtt
import os
from rich import print
from bs4 import BeautifulSoup
import requests

# ✅ Import your chatbot (Gemini-powered)
from Backend.Chatbot import ChatBot

# ========= MQTT (IoT) CONFIG =========
MQTT_BROKER = "04fff2a5571b47729adc6fcd76c17bd0.s1.eu.hivemq.cloud"
MQTT_PORT = 8883
MQTT_USER = "hivemq.webclient.1741844782940"
MQTT_PASSWORD = "v2,7<B&k@9jKFLX8mewD"
BASE_TOPIC = "esp8266/devices"
device_names = ["light", "fan", "plug", "ac"]

mqtt_client = mqtt.Client()
mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
mqtt_client.tls_set()

# def on_connect(client, userdata, flags, rc):
#     if rc == 0:
#         print("[green]✅ Connected to MQTT broker[/green]")
#     else:
#         print("[red]❌ MQTT connection failed[/red]")

# mqtt_client.on_connect = on_connect
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.loop_start()

# ========== ACTUAL COMMANDS ==========

def GoogleSearch(topic):
    try:
        webbrowser.open(f"https://www.google.com/search?q={topic}")
        return True
    except:
        return False

def YoutubeSearch(topic):
    try:
        webbrowser.open(f"https://www.youtube.com/results?search_query={topic}")
        return True
    except:
        return False

def PlayYoutube(query):
    try:
        webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
        return True
    except:
        return False

def OpenApp(app):
    try:
        os.system(f"open -a '{app}'")
        return True
    except:
        try:
            webbrowser.open(f"https://www.{app}.com")
            return True
        except:
            return False

def CloseApp(app):
    try:
        os.system(f"pkill '{app}'")
        return True
    except:
        return False

# ✅ AI CONTENT WRITING + MAC TEXTEDIT
def Content(topic):
    os.makedirs("Data", exist_ok=True)

    prompt = f"Write a fully formatted, grammatically correct and professional document about: {topic}"
    ai_text = ChatBot(prompt)

    # ✅ Fallback: ensure text is not empty
    if not ai_text or ai_text.strip() == "":
        ai_text = f"Unable to auto-generate detailed content for: {topic}. Please refine the topic."

    file_name = topic.replace(" ", "_") + ".txt"
    path = f"Data/{file_name}"

    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(ai_text)

        # ✅ Mac version opens in TEXTEDIT
        os.system(f"open -a TextEdit '{path}'")
        return True

    except Exception as e:
        print("Content file error:", e)
        return False

# ✅ Mac Volume
def System(command):
    if command == "volume up":
        os.system("osascript -e 'set volume output volume (output volume of (get volume settings) + 10)'")
    elif command == "volume down":
        os.system("osascript -e 'set volume output volume (output volume of (get volume settings) - 10)'")
    elif command == "mute":
        os.system("osascript -e 'set volume output muted true'")
    elif command == "unmute":
        os.system("osascript -e 'set volume output muted false'")
    else:
        return False
    return True

# ✅ IoT device control
def control_device(device, state):
    if device not in device_names:
        return f"No such IoT device: {device}"

    message = f"{device} {state.upper()}"
    mqtt_client.publish(BASE_TOPIC, message)
    return f"IoT command sent: {message}"

# ========== MAIN AUTOMATION HANDLER ==========

async def TranslateAndExecute(commands: list[str]):
    actions = []
    for c in commands:
        c = c.lower()

        if c.startswith("open"):
            app = c.replace("open", "").strip()
            actions.append(asyncio.to_thread(OpenApp, app))

        elif c.startswith("close"):
            app = c.replace("close", "").strip()
            actions.append(asyncio.to_thread(CloseApp, app))

        elif c.startswith("play"):
            song = c.replace("play", "").strip()
            actions.append(asyncio.to_thread(PlayYoutube, song))

        elif c.startswith("google search"):
            q = c.replace("google search", "").strip()
            actions.append(asyncio.to_thread(GoogleSearch, q))

        elif c.startswith("youtube search"):
            q = c.replace("youtube search", "").strip()
            actions.append(asyncio.to_thread(YoutubeSearch, q))

        elif c.startswith("content"):
            topic = c.replace("content", "").strip()
            actions.append(asyncio.to_thread(Content, topic))

        elif c.startswith("system"):
            com = c.replace("system", "").strip()
            actions.append(asyncio.to_thread(System, com))

        elif c.startswith("iot"):
            parts = c.replace("iot", "").strip().split()
            if len(parts) == 2:
                dev, state = parts
                actions.append(asyncio.to_thread(control_device, dev, state))

    return await asyncio.gather(*actions, return_exceptions=True)

async def Automation(commands: list[str]):
    await TranslateAndExecute(commands)
    return True
