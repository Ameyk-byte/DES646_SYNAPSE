# desktop_app.py — Neuro Desktop App (Gemini + Mac/Windows)
import sys, os, html, webbrowser, threading , asyncio
from PyQt5 import QtCore, QtGui, QtWidgets

# Correct backend imports
from Backend.SpeechToText import SpeechRecognition
from Backend.TextToSpeech import TextToSpeech
from Backend.Model import FirstLayerDMM
from Backend.Chatbot import ChatBot
from Backend.ImageGenration import GenerateImage
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.IoT import iot
from Backend.Learning import run as LearningRecommender

def is_mac():
    return sys.platform.startswith("darwin")

def is_win():
    return sys.platform.startswith("win")


# ---------------- Backend Adapter ----------------
class BackendAdapter:
    def listen_once(self):
        try:
            text = SpeechRecognition()
            return text if text else "[No speech detected]"
        except Exception as e:
            return f"[Speech Error: {e}]"

    def speak(self, text):
        try:
            TextToSpeech(text)
        except:
            pass

    def classify(self, query: str):
        try:
            decisions = FirstLayerDMM(query)
            return decisions
        except Exception:
            return ["general " + query]

    def answer_general(self, query: str):
        try:
            return ChatBot(query)
        except Exception as e:
            return f"Chatbot error: {e}"


# --------------- Worker Thread ---------------
class Worker(QtCore.QObject):
    finished = QtCore.pyqtSignal(str)

    def __init__(self, backend, query):
        super().__init__()
        self.backend = backend
        self.query = query

    @QtCore.pyqtSlot()
    def run(self):
        decisions = self.backend.classify(self.query)
        d = decisions[0]

        # Learning Recommender
        if d.startswith("LearningRecommender"):
            text, payload = LearningRecommender(self.query)
            result = f"📚 {text}"
            self.finished.emit(result)
            return

        # Image generation
        if d.startswith("generate image"):
            prompt = d.replace("generate image ", "")
            GenerateImage(prompt)
            self.finished.emit("🖼 Image generated successfully.")
            return

        # IoT
        if d.startswith("iot"):
            cmd = d.replace("iot ", "")
            ans = iot(cmd)
            self.finished.emit(f"🔧 {ans}")
            return

        # Automation tasks
        if any(d.startswith(x) for x in ["open","close","play","system"] for d in decisions):
            try:
                asyncio.run(Automation(decisions))
            except RuntimeError:
        # If event loop already running (PyQt case)
                loop = asyncio.get_event_loop()
                loop.create_task(Automation(decisions))
        
            self.finished.emit(intent, "Task executed.")
            return

        # Real-time search
        if d.startswith("realtime"):
            ans = RealtimeSearchEngine(self.query)
            self.finished.emit(ans)
            return

        # General Chatbot
        ans = self.backend.answer_general(self.query)
        self.finished.emit(ans)


# --------------- UI Window ---------------
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, backend):
        super().__init__()
        self.backend = backend

        self.setWindowTitle("Neuro AI Assistant")
        self.resize(950, 650)

        try:
            icon_path = os.path.join("logo.png")
            if os.path.exists(icon_path):
                self.setWindowIcon(QtGui.QIcon(icon_path))
        except:
            pass

        root = QtWidgets.QWidget()
        self.setCentralWidget(root)

        self.chat = QtWidgets.QTextEdit()
        self.chat.setReadOnly(True)

        self.input = QtWidgets.QLineEdit()
        self.input.setPlaceholderText("Ask Neuro…")

        self.sendBtn = QtWidgets.QPushButton("Send")
        self.micBtn = QtWidgets.QPushButton("🎤 Speak")
        self.clearBtn = QtWidgets.QPushButton("Clear")

        layout = QtWidgets.QVBoxLayout(root)
        layout.addWidget(self.chat)

        h = QtWidgets.QHBoxLayout()
        h.addWidget(self.input)
        h.addWidget(self.sendBtn)
        h.addWidget(self.micBtn)
        h.addWidget(self.clearBtn)
        layout.addLayout(h)

        self.sendBtn.clicked.connect(self.on_send)
        self.micBtn.clicked.connect(self.on_mic)
        self.clearBtn.clicked.connect(self.on_clear)
        self.input.returnPressed.connect(self.on_send)

        self.say_assistant("✅ Neuro desktop app started!")

    def say_user(self, text):
        self.chat.append(f"<b>You:</b> {html.escape(text)}")

    def say_assistant(self, text):
        self.chat.append(f"<b style='color:#00eaff'>Neuro:</b> {html.escape(text)}")

    def on_send(self):
        msg = self.input.text().strip()
        if not msg:
            return
        self.input.clear()
        self.say_user(msg)
        self.run_query(msg)

    def on_mic(self):
        self.say_assistant("🎤 Listening…")
        threading.Thread(target=self._mic_thread, daemon=True).start()

    def _mic_thread(self):
        heard = self.backend.listen_once()
        QtCore.QMetaObject.invokeMethod(
            self, "_mic_done", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(str, heard)
        )

    @QtCore.pyqtSlot(str)
    def _mic_done(self, heard):
        if not heard or heard.startswith("["):
            self.say_assistant(heard)
            return
        self.say_user(heard)
        self.run_query(heard)

    def on_clear(self):
        self.chat.clear()
        self.say_assistant("✔ Chat cleared.")

    def run_query(self, query):
        self.say_assistant("Thinking…")
        self.thread = QtCore.QThread()
        self.worker = Worker(self.backend, query)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_result)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def on_result(self, answer):
        self.say_assistant(answer)
        self.backend.speak(answer)


# -------- MAIN --------
def main():
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow(BackendAdapter())
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
p