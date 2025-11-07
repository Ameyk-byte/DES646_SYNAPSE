import sys
import threading
import json
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.Learning import run as LearningRecommender
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.Model import FirstLayerDMM
from Backend.ImageGenration import GenerateImage
from Backend.IoT import iot
from Backend.TextToSpeech import TextToSpeech


class NeuroApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Neuro AI Assistant")
        self.setGeometry(200, 150, 950, 650)
        self.setStyleSheet("background-color: #0f0f17;")

        layout = QHBoxLayout()

        # -----------------------
        # LEFT SIDE: CHAT AREA
        # -----------------------
        chatLayout = QVBoxLayout()

        title = QLabel("🤖 Neuro – AI Personal Assistant")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size:24px; font-weight: bold; 
            color:#00eaff; 
            margin: 10px;
        """)
        chatLayout.addWidget(title)

        self.outputBox = QTextEdit()
        self.outputBox.setReadOnly(True)
        self.outputBox.setStyleSheet("""
            background: rgba(25,25,40,0.8);
            border-radius: 10px;
            padding: 10px;
            color:white;
            font-size:15px;
        """)
        chatLayout.addWidget(self.outputBox)

        inputLayout = QHBoxLayout()
        self.inputField = QLineEdit()
        self.inputField.setPlaceholderText("Type here...")
        self.inputField.setStyleSheet("""
            font-size:16px; 
            padding:10px;
            border-radius: 6px;
            background:#1f1f2e; 
            color:white;
        """)
        inputLayout.addWidget(self.inputField)

        sendBtn = QPushButton("Send")
        sendBtn.clicked.connect(self.send_text)
        sendBtn.setStyleSheet(self.glowButton("#0078ff"))
        inputLayout.addWidget(sendBtn)

        micBtn = QPushButton("🎤 Speak")
        micBtn.clicked.connect(self.speech_to_text)
        micBtn.setStyleSheet(self.glowButton("#ff0055"))
        inputLayout.addWidget(micBtn)

        chatLayout.addLayout(inputLayout)

        layout.addLayout(chatLayout, 65)

        # -----------------------
        # RIGHT SIDE: LEARNING PANEL
        # -----------------------
        self.learningPanel = QVBoxLayout()

        self.learningTitle = QLabel("📚 Learning Recommendations")
        self.learningTitle.setStyleSheet("""
            font-size:20px; color:#00eaff; font-weight:bold;
            margin-bottom: 8px;
        """)

        self.learningList = QListWidget()
        self.learningList.setStyleSheet("""
            background: rgba(25,25,40,0.8);
            border-radius:8px;
            color:white;
            font-size:14px;
        """)

        self.exportBtn = QPushButton("📄 Export Study Plan (PDF)")
        self.exportBtn.clicked.connect(self.export_pdf)
        self.exportBtn.setVisible(False)
        self.exportBtn.setStyleSheet(self.glowButton("#00b359"))

        self.learningPanel.addWidget(self.learningTitle)
        self.learningPanel.addWidget(self.learningList)
        self.learningPanel.addWidget(self.exportBtn)

        sideWidget = QWidget()
        sideWidget.setLayout(self.learningPanel)
        sideWidget.setMaximumWidth(300)

        layout.addWidget(sideWidget, 35)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.studyPlan = []   # stores weekly plan for PDF export


    def glowButton(self, color):
        return f"""
            QPushButton {{
                background: {color};
                color: white;
                border-radius: 6px;
                padding: 8px;
                font-size: 15px;
            }}
            QPushButton:hover {{
                background: white;
                color: {color};
                font-weight:bold;
            }}
        """


    # -------------------------------------------
    # TEXT & VOICE HANDLERS
    # -------------------------------------------
    def send_text(self):
        text = self.inputField.text().strip()
        self.inputField.clear()
        if text:
            self.process_query(text)

    def speech_to_text(self):
        self.outputBox.append("🎙 Listening...")
        threading.Thread(target=self._speech_thread).start()

    def _speech_thread(self):
        text = SpeechRecognition()
        if text:
            self.outputBox.append(f"🗣 You: {text}")
            if "neuro" in text.lower():
                cleaned = text.lower().replace("neuro", "").strip()
                self.process_query(cleaned)
            else:
                self.outputBox.append("⚠️ Wake word not detected.")


    # -------------------------------------------
    # MAIN QUERY PROCESSOR
    # -------------------------------------------
    def process_query(self, query):
        self.outputBox.append(f"🧑 You: {query}")
        threading.Thread(target=self._process_thread, args=(query,)).start()

    def _process_thread(self, query):
        try:
            decisions = FirstLayerDMM(query)

            # ✅ Learning Recommender
            if any(d.startswith("LearningRecommender") for d in decisions):
                text, payload = LearningRecommender(query)
                self.outputBox.append(f"📚 Recommendations:\n{text}")
                TextToSpeech("Here are learning resources")

                self.update_learning_ui(payload)
                return

            # ✅ Real-time search
            if any(d.startswith("realtime") for d in decisions):
                ans = RealtimeSearchEngine(query)
                self.outputBox.append(f"🌍 {ans}")
                TextToSpeech(ans)
                return

            # ✅ Image generation
            for d in decisions:
                if d.startswith("generate image"):
                    prompt = d.replace("generate image ", "")
                    GenerateImage(prompt)
                    self.outputBox.append("🖼 Image Generated!")
                    TextToSpeech("Image generated.")
                    return

            # ✅ IoT
            for d in decisions:
                if d.startswith("iot"):
                    cmd = d.replace("iot ", "")
                    ans = iot(cmd)
                    self.outputBox.append(f"🔧 {ans}")
                    TextToSpeech(ans)
                    return

            # ✅ Automation
            if any(d.startswith(x) for x in ["open","close","play","system"] for d in decisions):
                Automation(decisions)
                self.outputBox.append("✅ Task executed.")
                TextToSpeech("Task done.")
                return

            # ✅ Default Chatbot
            answer = ChatBot(query)
            self.outputBox.append(f"🤖 Neuro: {answer}")
            TextToSpeech(answer)

        except Exception as e:
            self.outputBox.append("❌ Error occurred")
            print(e)


    # -------------------------------------------
    # UPDATE LEARNING PANEL
    # -------------------------------------------
    def update_learning_ui(self, payload):
        self.learningList.clear()
        self.studyPlan = payload.get("weekly_plan", [])
        recs = payload.get("recommendations", [])

        for r in recs:
            item = QListWidgetItem(f"{r['title']} ({r['level']}) - {r['duration_min']} min")
            item.setToolTip(r['url'])
            self.learningList.addItem(item)

        self.exportBtn.setVisible(True)


    # -------------------------------------------
    # EXPORT STUDY PLAN TO PDF
    # -------------------------------------------
    def export_pdf(self):
        file, _ = QFileDialog.getSaveFileName(self, "Save Study Plan", "study_plan.pdf", "PDF Files (*.pdf)")
        if not file:
            return

        c = canvas.Canvas(file, pagesize=A4)
        c.setFont("Helvetica-Bold", 18)
        c.drawString(50, 800, "Neuro – Personalized Study Plan")

        y = 760
        c.setFont("Helvetica", 12)

        for wk in self.studyPlan:
            c.drawString(50, y, f"Week {wk['week']}:")
            y -= 20
            for item in wk["items"]:
                c.drawString(60, y, f"- {item['title']} | {item['type']} | {item['duration_min']} min")
                y -= 18
            y -= 10

        c.save()
        self.outputBox.append("✅ Study plan PDF saved!")
        TextToSpeech("Study plan exported successfully.")


# ----------------------------
# RUN APP
# ----------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NeuroApp()
    window.show()
    sys.exit(app.exec_())
