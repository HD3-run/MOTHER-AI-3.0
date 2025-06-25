import sys
import os
import webbrowser
from flask import Flask, render_template, request, jsonify

from memory.structured_store import init_db
from processing.llm_handler import get_response
from processing.context_builder import build_prompt_with_context
from personality.loader import load_config
from utils.usage_tracker import log_user_input, log_response
from memory.vector_store import add_memory
from memory.episodic_logger import log_event
from utils.sentiment import get_sentiment
from utils.logger import log_event as debug_log

# Initialize Flask
app = Flask(__name__)
config = load_config()
init_db()

@app.route("/")
def home():
    return render_template("index.html", assistant_name=config['name'])

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "").strip()

    if not user_input:
        return jsonify({"error": "Empty message"}), 400

    try:
        log_user_input()
        prompt = build_prompt_with_context(user_input, config)
        raw_response = get_response(prompt, config)
        log_response()

        # Save memory
        add_memory(user_input, raw_response)
        log_event(user_input, raw_response)
        debug_log(f"Sentiment: {get_sentiment(user_input)}")

        return jsonify({"response": raw_response})

    except Exception as e:
        print("[SERVER ERROR]", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("🌐 Launching MOTHER Web UI...")
    print("🧠 Python sys.path:")
    for p in sys.path:
        print(" -", p)

    try:
        # Open browser after short delay
        import threading
        threading.Timer(1.5, lambda: webbrowser.open("http://localhost:5000")).start()

        # Run Flask server
        app.run(port=5000, debug=True)

    except Exception as e:
        print("[FATAL] Failed to launch web server:", e)
