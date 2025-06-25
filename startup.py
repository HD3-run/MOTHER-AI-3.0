# utils/startup.py

from memory.structured_store import init_db

def initialize_mother():
    print("🧠 Initializing MOTHER's brain...")
    init_db()
    print("✅ Structured memory initialized.")
