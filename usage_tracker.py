import json
import os
from datetime import datetime

TRACKER_PATH = "data/usage_log.json"

def load_usage():
    if not os.path.exists(TRACKER_PATH):
        return {
            "total_user_inputs": 0,
            "total_responses": 0,
            "last_updated": str(datetime.today().date())
        }

    with open(TRACKER_PATH, "r") as f:
        return json.load(f)


def save_usage(usage_data):
    os.makedirs(os.path.dirname(TRACKER_PATH), exist_ok=True)
    with open(TRACKER_PATH, "w") as f:
        json.dump(usage_data, f, indent=4)


def log_user_input():
    data = load_usage()
    data["total_user_inputs"] += 1
    data["last_updated"] = str(datetime.today().date())
    save_usage(data)


def log_response():
    data = load_usage()
    data["total_responses"] += 1
    data["last_updated"] = str(datetime.today().date())
    save_usage(data)


def get_usage_summary():
    data = load_usage()
    return f"You've sent {data['total_user_inputs']} messages and MOTHER has replied {data['total_responses']} times."
