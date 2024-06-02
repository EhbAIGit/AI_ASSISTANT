import pyttsx3
from datetime import datetime
import time



def text_to_speech(text, filename, voice_id=None):
    engine = pyttsx3.init()
    if voice_id:
        engine.setProperty('voice', voice_id)
    engine.save_to_file(text, filename)
    engine.runAndWait()

# Example text
text = ("Hello! You have reached our automated answering machine. We have successfully recorded your message. Thank you for getting in touch with us. We will get back to you shortly. ""Have a great day!")
filename = "response.mp3"

engine = pyttsx3.init()

# Get the available voices
voices = engine.getProperty('voices')

# List the voices
for index, voice in enumerate(voices):
    print(f"Voice {index}:")
    print(f" - ID: {voice.id}")
    print(f" - Name: {voice.name}")
    print(f" - Languages: {voice.languages}")
    print(f" - Gender: {voice.gender}")
    print(f" - Age: {voice.age}")
    print()
# Set the voice ID (replace 'voice_id' with the actual ID you want to use)
voice_id = "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0"  # Example for macOS

text_to_speech(text, filename, voice_id)
