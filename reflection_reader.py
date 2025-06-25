import os
from datetime import datetime

def get_reflection_for_date(date_str):
    # Path: reflection/mother_2025-06-21.log
    log_path = f"reflection/mother_{date_str}.log"
    if not os.path.exists(log_path):
        return f"I don't have a reflection log for {date_str}. Maybe we didn’t talk that day."

    with open(log_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    user_lines = [line.strip() for line in lines if "User:" in line]
    ai_lines = [line.strip() for line in lines if "MOTHER:" in line]

    summary = f"Here’s what I remember from {date_str}:\n"
    for i in range(min(3, len(user_lines))):
        summary += f"{user_lines[i]} -> {ai_lines[i] if i < len(ai_lines) else '...'}\n"
    return summary
