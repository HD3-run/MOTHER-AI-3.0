import re

def detect_intent(user_input):
    input_lower = user_input.lower()

    if any(phrase in input_lower for phrase in ["learn this", "let me teach you", "remember this"]):
        return "learn"
    elif any(phrase in input_lower for phrase in ["that's wrong", "you're wrong", "actually", "correction"]):
        return "correction"
    elif any(phrase in input_lower for phrase in ["what did we do", "write a reflection", "journal", "summary of", "remember", "what happened", "tell me about"]):
        return "reflect"
    elif any(phrase in input_lower for phrase in ["how do i look", "do i look good", "what do you see"]):
        return "visual_check"
    else:
        return "chat"