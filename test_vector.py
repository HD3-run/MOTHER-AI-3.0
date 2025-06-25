from memory.vector_store import add_memory, search_similar_memories

add_memory("Where do I live?", "You live in Kolkata.")
print(search_similar_memories("Where am I from?"))
