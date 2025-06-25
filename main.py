# main.py

import sys
import os

# Ensure project root is in sys.path
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, 'reflection'))

print("🧠 Python sys.path:")
for p in sys.path:
    print(" -", p)

# Ensure data folder exists
DATA_DIR = os.path.join(BASE_DIR, "data")
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
    print(f"[DEBUG] Created data directory: {DATA_DIR}")

# Import core MOTHER components
from memory.structured_store import init_db
from personality.loader import load_config
from gui.main_window import launch_gui
from reflection.reflection_engine import summarize_day
from reflection.journal_writer import write_reflection


def main():
    print("[DEBUG] Initializing database...")
    init_db()

    print("[DEBUG] Loading configuration...")
    config = load_config()

    try:
        print("[DEBUG] Launching GUI...")
        launch_gui(config)
    except Exception as e:
        print("[CRITICAL] MOTHER crashed during GUI execution:", e)
    finally:
        print("[DEBUG] Session ending — summarizing reflection...")
        try:
            summary = summarize_day()
            write_reflection(summary)
            print("[DEBUG] Reflection written.")
        except Exception as e:
            print("[ERROR] Failed to write reflection:", e)

if __name__ == "__main__":
    main()

# main.py (web version)
from flask import Flask
from app.routes import chat_api

app = Flask(__name__)
app.register_blueprint(chat_api)

if __name__ == '__main__':
    app.run(debug=True)

