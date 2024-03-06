import sounddevice as sd
import numpy as np

def print_audio_devices():
    # Haal de lijst met beschikbare audio-apparaten op
    audio_devices = sd.query_devices()

    print("Beschikbare audio-apparaten:")
    for i, device in enumerate(audio_devices):
        print(f"{i + 1}. {device['name']} (type: {device['hostapi']}), Kanalen: {device['max_input_channels']}, Samplefrequentie: {device['default_samplerate']} Hz")

# Roep de functie aan om de beschikbare audio-apparaten weer te geven
print_audio_devices()