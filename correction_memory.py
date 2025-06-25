import os
import json

CORRECTION_FILE = os.path.join("data", "corrections.json")
os.makedirs("data", exist_ok=True)

# Ensure the file exists
if not os.path.exists(CORRECTION_FILE):
    with open(CORRECTION_FILE, "w") as f:
        json.dump([], f)

def add_correction(wrong_response, correct_response, context=None):
    correction = {
        "wrong": wrong_response,
        "correct": correct_response,
        "context": context
    }

    with open(CORRECTION_FILE, "r") as f:
        data = json.load(f)

    data.append(correction)

    with open(CORRECTION_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_all_corrections():
    with open(CORRECTION_FILE, "r") as f:
        return json.load(f)