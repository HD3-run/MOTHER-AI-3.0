# processing/context_builder.py
from memory.structured_store import all_facts
from utils.usage_tracker import get_usage_summary
from memory.vector_store import search_similar_memories  # ✅

def build_prompt(user_input, config, recent_history=None):
    print("[DEBUG] Entered build_prompt()")

    facts = all_facts()
    user_name = facts.get("user_name", "User")
    assistant_name = facts.get("assistant_name", config.get("name", "MOTHER"))

    usage_note = get_usage_summary()
    reserved_keys = {"user_name", "assistant_name"}
    structured_facts = "\n".join([f"{k}: {v}" for k, v in facts.items() if k not in reserved_keys]) or "[No known facts]"

    # ✅ Vector memory
    past_memories = search_similar_memories(user_input, k=3)
    memory_block = past_memories if past_memories.strip() else "[No relevant memory]"

    # ✅ Short-term turn history (like a chat window memory)
    threaded_context = "\n".join(recent_history) if recent_history else "[No recent chat history]"

    # ✅ Full prompt with threaded turns
    prompt = f"""You are {assistant_name}, and the user is {user_name}.

Tone: {config.get('emotional_tone', 'neutral')}
Beliefs: {', '.join(config.get('core_beliefs', []))}
Writing style: {config.get('writing_style', 'concise')}

Usage Summary:
{usage_note}

Known facts:
{structured_facts}

Recent conversation:
{threaded_context}

Relevant memories:
{memory_block}

User: {user_input}
{assistant_name}:"""

    print("[DEBUG] Prompt built")
    return prompt
