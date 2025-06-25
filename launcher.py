# app/launcher.py

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
print("[DEBUG] sys.path =", sys.path)

from flask import Flask
from app.routes import chat_api

app = Flask(__name__, template_folder="templates", static_folder="static")
app.register_blueprint(chat_api)

if __name__ == "__main__":
    print("[🚀] Starting MOTHER Web UI...")
    app.run(debug=True, port=5000)

import threading
import webbrowser
import time
import subprocess

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def launch_flask():
    subprocess.run(["python", "app/routes.py"])

if __name__ == "__main__":
    print("[🚀] Starting MOTHER Web UI...")
    threading.Thread(target=launch_flask, daemon=True).start()
    time.sleep(2)
    webbrowser.open("http://localhost:5000")
