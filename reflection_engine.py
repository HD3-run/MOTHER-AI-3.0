import os
from datetime import datetime
from memory.episodic_logger import get_today_log
from memory.structured_store import all_facts
from rake_nltk import Rake

def summarize_day():
    entries = get_today_log()
    facts = all_facts()

    summary_lines = [
        f"🧠 Reflection for {datetime.now().strftime('%A, %B %d, %Y')}",
        "-" * 40
    ]

    if entries:
        all_text = ""
        for entry in entries:
            user = entry.get("user_input", "")
            response = entry.get("mother_response", "")
            all_text += user + " " + response + " "
        r = Rake()
        r.extract_keywords_from_text(all_text)
        keywords = r.get_ranked_phrases()[:5]
        summary_lines.append("\nTopics discussed today: " + ", ".join(keywords))
        summary_lines.append("\nWhat happened today:")
        for entry in entries:
            time = entry.get("timestamp", "unknown time")
            user = entry.get("user_input", "")
            response = entry.get("mother_response", "")
            summary_lines.append(f"{time} — You said: {user}")
            summary_lines.append(f"{time} — I said: {response}\n")
    else:
        summary_lines.append("\nI didn’t have any interactions today. Hopefully tomorrow will be more interesting.")

    if facts:
        summary_lines.append("\n📓 What I learned about you:")
        for k, v in facts.items():
            summary_lines.append(f" - {k}: {v}")

    summary_lines.append("\nThat’s everything I remember from today. I’ll reflect more as I grow.")
    return "\n".join(summary_lines)