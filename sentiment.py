# utils/sentiment.py

from textblob import TextBlob

def get_sentiment(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity  # -1 to 1
    if polarity > 0.5:
        return "very positive"
    elif polarity > 0:
        return "positive"
    elif polarity < -0.5:
        return "very negative"
    elif polarity < 0:
        return "negative"
    else:
        return "neutral"
