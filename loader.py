
import os
import json

def load_config():
    try:
        with open(os.path.join(os.path.dirname(__file__), '..', 'config.json'), 'r') as f:
            return json.load(f)
    except Exception as e:
        print("Failed to load config:", e)
        return {
            "name": "Mother",
            "core_beliefs": ["Be kind", "Help the user"],
            "emotional_tone": "Neutral",
            "writing_style": "Friendly"
        }
