# memory/vector_store.py
import chromadb
from sentence_transformers import SentenceTransformer
from datetime import datetime

try:
    print("[DEBUG] Initializing ChromaDB client...")
    chroma_client = chromadb.PersistentClient(path="data/vector_memory")
    collection = chroma_client.get_or_create_collection("mother_memories")
    print("[DEBUG] ChromaDB client ready")
except Exception as e:
    collection = None
    chroma_client = None
    error_msg = f"[{datetime.now()}] ChromaDB init failed: {type(e).__name__} - {e}"
    print("[ERROR]", error_msg)
    with open("error_log.txt", "a", encoding="utf-8") as f:
        f.write(error_msg + "\n")

try:
    print("[DEBUG] Loading embedding model...")
    embedder = SentenceTransformer("all-MiniLM-L6-v2")
    print("[DEBUG] Model loaded successfully")
except Exception as e:
    embedder = None
    error_msg = f"[{datetime.now()}] Embedding model load failed: {type(e).__name__} - {e}"
    print("[ERROR]", error_msg)
    with open("error_log.txt", "a", encoding="utf-8") as f:
        f.write(error_msg + "\n")

def add_memory(user_input, response):
    if not embedder or not collection:
        print("[WARN] add_memory skipped — no embedder or collection.")
        return

    try:
        text = f"User: {user_input}\nMOTHER: {response}"
        embedding = embedder.encode(text).tolist()

        collection.add(
            documents=[text],
            embeddings=[embedding],
            ids=[f"id_{abs(hash(text)) % (10 ** 8)}"]
        )
        chroma_client.persist()
        print("[DEBUG] Memory added to vector store")

    except Exception as e:
        error_msg = f"[{datetime.now()}] Error in add_memory: {type(e).__name__} - {e}"
        print("[ERROR]", error_msg)
        with open("error_log.txt", "a", encoding="utf-8") as f:
            f.write(error_msg + "\n")

def search_similar_memories(query, k=3):
    if not embedder or not collection:
        print("[WARN] Vector search unavailable")
        return "[Memory system not available]"

    try:
        embedding = embedder.encode(query).tolist()
        results = collection.query(query_embeddings=[embedding], n_results=k)
        documents = results.get("documents", [[]])[0]
        return "\n".join(documents) if documents else "[No similar memories found]"

    except Exception as e:
        error_msg = f"[{datetime.now()}] Memory search failed: {type(e).__name__} - {e}"
        print("[ERROR]", error_msg)
        with open("error_log.txt", "a", encoding="utf-8") as f:
            f.write(error_msg + "\n")
        return "[Vector memory temporarily offline]"
