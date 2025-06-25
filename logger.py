# utils/logger.py

import os
from utils.timestamp import get_timestamp

LOG_FILE = os.path.join("data", "mother_log.txt")
os.makedirs("data", exist_ok=True)

def log_event(event):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{get_timestamp()}] {event}\n")
