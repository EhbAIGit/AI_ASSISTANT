import sounddevice as sd
import numpy as np
import tempfile
from scipy.io.wavfile import write

def rms(frame):
    """
    Bereken de root mean square van de audio frame.
    """
    return np.sqrt(np.mean(np.square(frame), axis=0))

def record_until_silence(threshold=0.0001, fs=44100, chunk_size=1024, max_silence=5):
    """
    Neemt audio op zolang er geluid is boven een bepaalde drempelwaarde en stopt na een bepaalde periode van stilte.
    :param threshold: De drempelwaarde voor het volume om te stoppen met opnemen.
    :param fs: Samplefrequentie.
    :param chunk_size: Het aantal samples per frame.
    :param max_silence: Maximale tijd in seconden om te wachten tijdens stilte voordat de opname stopt.
    :return: Pad naar het opgeslagen audiobestand.
    """
    print("Begin met opnemen... Spreek nu.")
    recorded_frames = []
    silent_frames = 0
    silence_limit = int(max_silence * fs / chunk_size)  # Aantal frames van stilte voordat opname stopt

    def callback(indata, frames, time, status):
        nonlocal silent_frames
        volume_norm = rms(indata)
        if volume_norm < threshold:
            silent_frames += 1
            if silent_frames > silence_limit:
                raise sd.CallbackStop
        else:
            silent_frames = 0
        recorded_frames.append(indata.copy())

    with sd.InputStream(callback=callback, device=1, dtype='float32', channels=1, samplerate=fs, blocksize=chunk_size):
        print("Opname gestart. Wacht op geluid...")
        sd.sleep(10000)  # Wacht maximaal 10 seconden voor geluid

    print("\nEinde van de opname.")
    recording = np.concatenate(recorded_frames, axis=0)

    # Tijdelijk bestand aanmaken en opname opslaan
    temp_file = tempfile.mktemp(prefix='opgenomen_audio_', suffix='.wav')
    write(temp_file, fs, recording)  # Schrijf de opname naar een WAV-bestand

    print(f"Audio opgenomen en opgeslagen in: {temp_file}")
    return temp_file

# Opname starten
audio_file_path = record_until_silence()


 

from openai import OpenAI

client = OpenAI()

with open(audio_file_path, "rb") as audio_file:
    transcript = client.audio.transcriptions.create(
      model="whisper-1", 
      file=audio_file
    )
    print(transcript)

