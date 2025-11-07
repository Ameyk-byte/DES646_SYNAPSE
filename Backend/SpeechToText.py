# Backend/SpeechToText.py  (Mac-safe)
import speech_recognition as sr
import sounddevice as sd
import soundfile as sf
import tempfile

DURATION_SEC = 4
SAMPLE_RATE = 44100

def SpeechRecognition():
    r = sr.Recognizer()
    try:
        # Record audio via sounddevice
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as tmp:
            print("🎤 Listening...")
            audio = sd.rec(int(DURATION_SEC * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype="float32")
            sd.wait()
            sf.write(tmp.name, audio, SAMPLE_RATE)

            with sr.AudioFile(tmp.name) as source:
                data = r.record(source)

        # Google Speech API (free, online)
        text = r.recognize_google(data)
        print("✅ Heard:", text)
        return text
    except Exception as e:
        print("Speech error:", e)
        return ""

