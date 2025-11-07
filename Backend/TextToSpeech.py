# Backend/TextToSpeech.py
import asyncio
import tempfile
import subprocess
import sys

from dotenv import dotenv_values
import edge_tts

env = dotenv_values(".env")
VOICE = env.get("TTS_VOICE", "en-US-AriaNeural")  # you can change the voice

async def _speak_async(text: str):
    # Synthesize to a temp mp3 and play via macOS 'afplay' (works reliably on Mac)
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=True) as f:
        output_path = f.name
        communicate = edge_tts.Communicate(text, VOICE)
        await communicate.save(output_path)
        try:
            # macOS default player
            subprocess.run(["afplay", output_path], check=False)
        except Exception:
            # As a fallback, print the text if afplay is unavailable
            print(text)

def TextToSpeech(text: str):
    try:
        asyncio.run(_speak_async(text))
    except RuntimeError:
        # If there's already a running loop (rare), fallback to direct print
        print(text)

if __name__ == "__main__":
    TextToSpeech("Hello! This is a test of the macOS safe text to speech.")
