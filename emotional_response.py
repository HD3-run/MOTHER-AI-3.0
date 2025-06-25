from memory.episodic_logger import get_recent_logs
from statistics import mean

def get_adaptive_tone():
    recent_logs = get_recent_logs(10)
    if not recent_logs:
        return "neutral"
    sentiments = [log["sentiment"] for log in recent_logs if "sentiment" in log]
    if not sentiments:
        return "neutral"
    sentiment_map = {
        "very positive": 2,
        "positive": 1,
        "neutral": 0,
        "negative": -1,
        "very negative": -2
    }
    numerical_sentiments = [sentiment_map.get(s, 0) for s in sentiments]
    average_sentiment = mean(numerical_sentiments)
    if average_sentiment > 1:
        return "very happy"
    elif average_sentiment > 0:
        return "happy"
    elif average_sentiment < -1:
        return "concerned"
    elif average_sentiment < 0:
        return "supportive"
    else:
        return "neutral"

def adjust_response_tone(response, tone=None):
    if tone is None:
        tone = get_adaptive_tone()
    if tone == "very happy":
        return f"{response} 😄 I'm really enjoying our conversation!"
    elif tone == "happy":
        return f"{response} 😊 It's great talking with you."
    elif tone == "concerned":
        return f"{response} 😟 Is everything okay? I'm here to help."
    elif tone == "supportive":
        return f"{response} 💖 I believe in you. Let's tackle this together."
    elif tone == "warm":
        return f"{response} 😊 I'm here if you need anything."
    elif tone == "funny":
        return f"{response} 😂 (Don't take me too seriously, but I mean it!)"
    elif tone == "flirty":
        return f"{response} 😏 Just saying, you look smart when you're curious."
    elif tone == "serious":
        return f"{response} This is important, so I wanted to be clear."
    else:
        return response