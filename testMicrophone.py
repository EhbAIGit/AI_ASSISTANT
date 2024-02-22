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

def rms(frame):
    """
    Bereken de root mean square van de audio frame.
    """
    return np.sqrt(np.mean(np.square(frame), axis=0))

def print_sound_level():
    """
    Print het huidige gemiddelde geluidsniveau tijdens de opname.
    """
    duration = 30  # Duur van de opname in seconden
    fs = 44100  # Samplefrequentie
    chunk_size = 1024  # Het aantal samples per frame

    def callback(indata, frames, time, status):
        volume_norm = rms(indata)
        if (volume_norm > 0.1) :
            print(f"Gemiddeld geluidsniveau: {np.mean(volume_norm):.4f}")  # Print het gemiddelde geluidsniveau
        if status:
            print(f"Status: {status}")

    with sd.InputStream(callback=callback, device=1, dtype='float32', channels=1, samplerate=fs, blocksize=chunk_size):
        print("Opname gestart...")
        sd.sleep(int(duration * 1000))  # Wacht tot de opname is voltooid

# Start de opname en print het geluidsniveau
print_sound_level()
