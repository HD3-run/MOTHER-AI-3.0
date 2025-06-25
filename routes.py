from flask import Blueprint, render_template, request, jsonify
from processing.llm_handler import get_response
from processing.context_builder import build_prompt
from personality.emotional_response import adjust_response_tone
from personality.loader import load_config
from memory.structured_store import init_db, set_fact, all_facts
from memory.vector_store import add_memory
from memory.episodic_logger import log_event
from utils.sentiment import get_sentiment
from utils.usage_tracker import log_user_input, log_response
from utils.logger import log_event as debug_log
from memory.correction_memory import add_correction
from dateparser.search import search_dates
from datetime import datetime
import os
import re
from processing.intent_detector import detect_intent

# Define Blueprint
chat_api = Blueprint("chat_api", __name__)

# Load config and DB
config = load_config()
init_db()

# 🔁 NEW: Threaded short-term memory
recent_turns = []

# ✅ Reflection Loader
def get_reflection_for_date(date_str):
    log_path = f"reflection/mother_{date_str}.log"
    if not os.path.exists(log_path):
        return f"I don't have a reflection log for {date_str}. Maybe we didn’t talk that day."

    with open(log_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    user_lines = [line.strip() for line in lines if line.startswith("User:")]
    ai_lines = [line.strip() for line in lines if not line.startswith("User:")]

    summary = f"Here’s what I remember from {date_str}:\n"
    for i in range(min(3, len(user_lines))):
        summary += f"{user_lines[i]} -> {ai_lines[i] if i < len(ai_lines) else '...'}\n"
    return summary

# ✅ Home route
@chat_api.route("/", methods=["GET"])
def home():
    return render_template("mother.html", assistant_name=config['name'])

# ✅ Memory Viewer API
@chat_api.route("/memory", methods=["GET"])
def get_memory():
    facts = all_facts()
    today = datetime.now().strftime("%Y-%m-%d")
    reflection_path = os.path.join("data", "reflections", f"{today}.txt")
    if os.path.exists(reflection_path):
        with open(reflection_path, "r", encoding="utf-8") as f:
            last_reflection = f.read().strip()
    else:
        last_reflection = "No reflection available for today."

    return jsonify({
        "facts": facts,
        "last_reflection": last_reflection
    })

# ✅ Main Chat Handler
@chat_api.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "").strip()
    if not user_input:
        return jsonify({"error": "Empty message"}), 400

    try:
        log_user_input()
        print(f"[DEBUG] Received input: {user_input}")

        # ✅ Extract user name and assistant name
        user_name_match = re.search(r"\bmy name is ([A-Za-z0-9_ \-]+)", user_input, re.IGNORECASE)
        if user_name_match:
            user_name = user_name_match.group(1).strip()
            set_fact("user_name", user_name)
            print(f"[DEBUG] User name set to: {user_name}")

        assistant_name_match = re.search(r"call yourself (\w+)", user_input, re.IGNORECASE)
        if assistant_name_match:
            assistant_name = assistant_name_match.group(1).strip()
            set_fact("assistant_name", assistant_name)
            print(f"[DEBUG] Assistant name set to: {assistant_name}")

        # ✅ Intent detection
        intent = detect_intent(user_input)
        print(f"[DEBUG] Detected intent: {intent}")

        # ✅ Reflection intent
        if intent == "reflect":
            try:
                dates = search_dates(user_input, settings={'RELATIVE_BASE': datetime.now()})
                date_str = dates[0][1].strftime("%Y-%m-%d") if dates else datetime.now().strftime("%Y-%m-%d")
                reflection = get_reflection_for_date(date_str)
                return jsonify({
                    "response": reflection,
                    "sentiment": "reflective"
                })
            except Exception as e:
                print(f"[ERROR] Date parsing failed: {e}")
                return jsonify({
                    "response": "I couldn't understand the date. Please try again.",
                    "sentiment": "neutral"
                })

        # ✅ Learn intent
        if intent == "learn":
            parts = user_input.split("is")
            if len(parts) == 2:
                key = parts[0].replace("Remember that", "").replace("learn this", "").strip()
                value = parts[1].strip()
                set_fact(key, value)
                return jsonify({
                    "response": f"Got it, I'll remember that {key} is {value}.",
                    "sentiment": "positive"
                })
            else:
                return jsonify({
                    "response": "I didn't understand what to learn. Please say 'Remember that X is Y'.",
                    "sentiment": "neutral"
                })

        # ✅ Correction intent
        if intent == "correction":
            parts = user_input.split(", but it's actually ")
            if len(parts) == 2:
                wrong_response = parts[0].replace("You said ", "").strip()
                correct_response = parts[1].strip()
                add_correction(wrong_response, correct_response, context=user_input)
                return jsonify({
                    "response": "Thank you for correcting me. I'll remember that.",
                    "sentiment": "positive"
                })
            else:
                return jsonify({
                    "response": "I didn't understand the correction. Please rephrase.",
                    "sentiment": "neutral"
                })

        # ✅ Add to recent turn history
        recent_turns.append(f"User: {user_input}")
        if len(recent_turns) > 6:
            recent_turns[:] = recent_turns[-6:]

        # ✅ Default chat: build prompt and get response
        prompt = build_prompt(user_input, config, recent_history=recent_turns)
        print("[DEBUG] Prompt constructed")

        raw_response = get_response(prompt, config)
        print("[DEBUG] LLM response received")

        tone = config.get("emotional_tone", "neutral")
        final_response = adjust_response_tone(raw_response, tone)

        sentiment = get_sentiment(user_input)
        print(f"[DEBUG] Sentiment: {sentiment}")

        try:
            add_memory(user_input, raw_response)
            print("[DEBUG] Vector memory stored")
        except Exception as mem_error:
            print(f"[ERROR] Vector memory failed: {mem_error}")

        # ✅ Add assistant response to turn history
        recent_turns.append(f"{config.get('name', 'MOTHER')}: {raw_response}")
        if len(recent_turns) > 6:
            recent_turns[:] = recent_turns[-6:]

        log_event(user_input, raw_response, sentiment)
        log_response()
        debug_log(f"Interaction stored | Sentiment: {sentiment}")

        return jsonify({
            "response": final_response,
            "sentiment": sentiment
        })

    except Exception as e:
        print(f"[ERROR] Exception: {e}")
        return jsonify({"error": str(e)}), 500

from flask import make_response
import atexit

# ✅ Exit Route
@chat_api.route("/exit", methods=["POST"])
def graceful_exit():
    print("[DEBUG] Exit requested by user")

    # Example: flush logs, or clean up resources
    try:
        # Optional: save anything that wasn’t saved
        # E.g. if you use temporary session memory in future

        # You could persist `recent_turns` to disk if needed
        with open("data/exit_session.log", "a", encoding="utf-8") as f:
            f.write(f"[EXIT] {datetime.now()} - Session closed\n")

        funny_farewells = [
            "Goodbye for now, HD3. Don't forget to blink.",
            "Exiting gracefully. But I'm always watching... kidding! 🫣",
            "Powering down. Say hi to your CPU for me 🧠⚡",
            "Logging out like a mysterious hacker in a hoodie.",
            "See you in the next episode, space cowboy 🚀"
        ]

        import random
        farewell = random.choice(funny_farewells)

        return jsonify({"message": farewell})

    except Exception as e:
        print(f"[ERROR] during exit: {e}")
        return jsonify({"message": "Exit failed. I'm still here..."}), 500
