import sqlite3
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "data", "structured_memory", "facts.db"))

def init_db():
    try:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS facts (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        conn.commit()
        print(f"[DEBUG] Facts DB initialized at {DB_PATH}")
    except Exception as e:
        print(f"[ERROR] Failed to initialize DB: {e}")
        with open("error_log.txt", "a", encoding="utf-8") as f:
            f.write(f"\n[{datetime.now()}] init_db() ERROR: {e}\n")
    finally:
        if 'conn' in locals():
            conn.close()

def set_fact(key, value):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('REPLACE INTO facts (key, value) VALUES (?, ?)', (key, value))
        conn.commit()
        print(f"[DEBUG] Fact set: {key} = {value}")
    except Exception as e:
        print(f"[ERROR] set_fact() failed: {e}")
        with open("error_log.txt", "a", encoding="utf-8") as f:
            f.write(f"\n[{datetime.now()}] set_fact('{key}') ERROR: {e}\n")
    finally:
        if 'conn' in locals():
            conn.close()

def get_fact(key):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT value FROM facts WHERE key=?', (key,))
        result = c.fetchone()
        return result[0] if result else None
    except Exception as e:
        print(f"[ERROR] get_fact() failed: {e}")
        with open("error_log.txt", "a", encoding="utf-8") as f:
            f.write(f"\n[{datetime.now()}] get_fact('{key}') ERROR: {e}\n")
        return None
    finally:
        if 'conn' in locals():
            conn.close()

def all_facts():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT key, value FROM facts')
        results = c.fetchall()
        facts = {k: v for k, v in results}
        print(f"[DEBUG] Loaded {len(facts)} structured facts")
        return facts
    except Exception as e:
        print(f"[ERROR] all_facts() failed: {e}")
        with open("error_log.txt", "a", encoding="utf-8") as f:
            f.write(f"\n[{datetime.now()}] all_facts() ERROR: {e}\n")
        return {}
    finally:
        if 'conn' in locals():
            conn.close()
