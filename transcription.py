# perception/transcription.py

import speech_recognition as sr

def transcribe_audio_file(file_path):
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(file_path) as source:
            audio = recognizer.record(source)
        text = recognizer.recognize_google(audio)
        return text
    except Exception as e:
        return f"[Error transcribing file: {e}]"
