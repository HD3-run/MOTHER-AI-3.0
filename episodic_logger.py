import os
import json
from datetime import datetime

EPISODIC_DIR = os.path.join("data", "episodic")
os.makedirs(EPISODIC_DIR, exist_ok=True)

def _get_today_file():
    date_str = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(EPISODIC_DIR, f"{date_str}.json")

def log_event(user_input, response, sentiment):
    entry = {
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "user_input": user_input,
        "mother_response": response,
        "sentiment": sentiment
    }

    today_file = _get_today_file()

    if os.path.exists(today_file):
        with open(today_file, "r") as f:
            data = json.load(f)
    else:
        data = []

    data.append(entry)

    with open(today_file, "w") as f:
        json.dump(data, f, indent=2)

def get_today_log():
    today_file = _get_today_file()
    if os.path.exists(today_file):
        with open(today_file, "r") as f:
            return json.load(f)
    else:
        return []

def get_recent_logs(n=10):
    today_file = _get_today_file()
    if os.path.exists(today_file):
        with open(today_file, "r") as f:
            data = json.load(f)
        return data[-n:]
    else:
        return []