# test_import.py

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

print("🧪 Trying import...")
from memory.vector_store import search_similar_memories

print("✅ Import succeeded!")
