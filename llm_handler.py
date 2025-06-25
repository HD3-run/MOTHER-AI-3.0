import requests
import traceback  # ✅ Needed for error logging

def get_response(user_input, config):
    system_prompt = f"""You are a warm, intelligent assistant named MOTHER.

Tone: {config.get('emotional_tone', 'neutral')}
Core beliefs: {', '.join(config.get('core_beliefs', []))}
Writing style: {config.get('writing_style', 'conversational')}

Always reply with empathy, personality, and understanding.
"""

    try:
        print("[LLM_HANDLER] Sending to Ollama /api/chat...")

        res = requests.post("http://localhost:11434/api/chat", json={
            "model": config.get("model", "llama3"),
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            "stream": False
        }, timeout=360)

        print("[LLM_HANDLER] Raw Ollama response:", res.text)

        if res.status_code != 200:
            print("[LLM_HANDLER ERROR] Status:", res.status_code)
            return f"[LLM Error: {res.status_code}]"

        data = res.json()
        message = data.get("message", {}).get("content", "").strip()

        if not message:
            print("[LLM_HANDLER] Warning: Empty message.")
            return "Hmm, I’m not sure how to respond to that."

        return message

    except Exception as e:
        print("[LLM_HANDLER EXCEPTION]", str(e))
        traceback.print_exc()
        with open("error_log.txt", "a", encoding="utf-8") as f:
            f.write("\n[ERROR] LLM request failed\n")
            traceback.print_exc(file=f)
        return "[LLM Error: Ollama is fucking with us]"
