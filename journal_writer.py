import os
from datetime import datetime

def write_reflection(summary):
    today = datetime.now().strftime("%Y-%m-%d")
    folder = os.path.join("data", "reflections")
    os.makedirs(folder, exist_ok=True)

    path = os.path.join(folder, f"{today}.txt")
    with open(path, "w", encoding="utf-8") as file:
        file.write(summary)