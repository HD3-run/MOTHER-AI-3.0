import sys
import re
import traceback
from datetime import datetime
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QVBoxLayout,
    QWidget, QLineEdit, QPushButton
)

from memory.structured_store import init_db, set_fact, all_facts
from processing.llm_handler import get_response
from processing.context_builder import build_prompt  # Reverted
from personality.emotional_response import adjust_response_tone
from memory.vector_store import add_memory
from memory.episodic_logger import log_event
from utils.sentiment import get_sentiment
from utils.logger import log_event as debug_log
from processing.intent_detector import detect_intent
from utils.usage_tracker import log_user_input, log_response, get_usage_summary

init_db()

class BackgroundWorker(QThread):
    finished = pyqtSignal()

    def __init__(self, user_input, raw_response):
        super().__init__()
        self.user_input = user_input
        self.raw_response = raw_response

    def run(self):
        try:
            add_memory(self.user_input, self.raw_response)
            print("[DEBUG] Memory added")
        except Exception as e:
            self.log_error("add_memory", e)

        try:
            log_event(self.user_input, self.raw_response)
            print("[DEBUG] Event logged")
        except Exception as e:
            self.log_error("log_event", e)

        try:
            sentiment = get_sentiment(self.user_input)
            debug_log(f"Sentiment: {sentiment}")
            print(f"[DEBUG] Sentiment logged: {sentiment}")
        except Exception as e:
            self.log_error("get_sentiment", e)

        self.finished.emit()

    def log_error(self, label, e):
        msg = f"[THREAD ERROR] {label}: {type(e).__name__} - {e}"
        print(msg)
        traceback.print_exc()
        with open("error_log.txt", "a", encoding="utf-8") as f:
            f.write(f"\n[{datetime.now()}] {msg}\n")
            traceback.print_exc(file=f)

class MotherWindow(QMainWindow):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.worker = None
        self.setWindowTitle(f"Talking to {config['name']}")
        self.setGeometry(100, 100, 640, 480)

        self.chat_box = QTextEdit()
        self.chat_box.setReadOnly(True)

        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("Say something...")
        self.input_box.returnPressed.connect(self.handle_input)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.handle_input)

        layout = QVBoxLayout()
        layout.addWidget(self.chat_box)
        layout.addWidget(self.input_box)
        layout.addWidget(self.send_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def handle_input(self):
        user_input = self.input_box.text().strip()
        if not user_input:
            return

        self.chat_box.append(f"You: {user_input}")
        self.input_box.clear()

        try:
            log_user_input()
            print("[DEBUG] User input received:", user_input)

            # Handle known structured memory commands
            if user_input.lower() == "show my memory":
                facts = all_facts()
                if not facts:
                    self.chat_box.append(f"{self.config['name']}: I haven’t learned anything about you yet.")
                    return

                explanation = {
                    "user_name": "so I can call you personally.",
                    "hobby": "to keep our conversations fun.",
                    "favorite_color": "in case you want styling or vibe suggestions.",
                    "birth_date": "to celebrate or remember your special day.",
                    "location": "to keep conversations relevant to your place.",
                    "favorite_food": "to suggest meals or ideas during chats.",
                    "favorite_position": "to have a fun no-strings conversation about intercourse positions."
                }

                response = f"{self.config['name']}: 🧠 Here's what I remember about you:\n"
                for key, value in facts.items():
                    reason = explanation.get(key, "to personalize our conversations.")
                    response += f"• {key} = {value} — {reason}\n"
                self.chat_box.append(response)
                return

            if "how many" in user_input.lower() and any(k in user_input.lower() for k in ["requests", "messages", "usage"]):
                usage = get_usage_summary()
                self.chat_box.append(f"{self.config['name']}: {usage}")
                return

            if re.match(r"(?i).*(my name is|call me)\s+([a-zA-Z]+)", user_input):
                name = re.findall(r"(?i)(?:my name is|call me)\s+([a-zA-Z]+)", user_input)[0]
                set_fact("user_name", name)
                self.chat_box.append(f"{self.config['name']}: Got it, {name}. I’ll remember your name!")
                return

            intent = detect_intent(user_input)
            print("[DEBUG] Intent detected:", intent)

            if intent == "reflect":
                from reflection.reflection_engine import summarize_day
                from reflection.journal_writer import write_reflection
                summary = summarize_day()
                write_reflection(summary)
                self.chat_box.append("MOTHER (Reflection):\n" + summary)
                return

            # Build simple prompt (no vector memory)
            prompt = build_prompt(user_input, self.config)
            print("[DEBUG] Prompt built")

            raw_response = get_response(prompt, self.config)
            log_response()

            tone = self.config.get("emotional_tone", "neutral")
            final_response = adjust_response_tone(raw_response, tone)
            cleaned = re.sub(r'[\x00-\x1F\x7F]', '', final_response.encode("utf-8", errors="replace").decode("utf-8"))

            self.chat_box.append(f"{self.config['name']}: {cleaned}")
            print("[DEBUG] Response displayed")

            # Launch thread
            self.worker = BackgroundWorker(user_input, raw_response)
            self.worker.finished.connect(self.cleanup_worker)
            self.worker.start()

        except Exception as e:
            self.report_crash("handle_input", e, user_input)

    def cleanup_worker(self):
        print("[DEBUG] BackgroundWorker finished")
        self.worker = None

    def report_crash(self, where, exception, user_input=""):
        msg = f"[{where.upper()} CRASH] {type(exception).__name__}: {exception}"
        print(msg)
        self.chat_box.append(msg)
        traceback.print_exc()
        with open("error_log.txt", "a", encoding="utf-8") as f:
            f.write(f"\n[{datetime.now()}] {msg}\nInput: {user_input}\n")
            traceback.print_exc(file=f)

def launch_gui(config):
    app = QApplication(sys.argv)
    window = MotherWindow(config)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    from config_loader import load_config
    config = load_config()
    launch_gui(config)
