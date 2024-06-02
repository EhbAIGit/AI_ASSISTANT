from pydub import AudioSegment
from pydub.playback import play
import numpy as np

# Functie om een noot te genereren
def create_tone(frequency, duration, volume=0.5):
    sample_rate = 44100
    num_samples = int(sample_rate * duration)
    x = np.linspace(0, duration, num_samples, False)
    tone = np.sin(frequency * x * 2 * np.pi) * volume
    audio = np.int16(tone * 32767).tobytes()
    return AudioSegment(
        audio, frame_rate=sample_rate, sample_width=2, channels=1
    )

# Frequenties van de noten in de melodie
notes_freq = {
    'C': 261.63,
    'D': 293.66,
    'E': 329.63,
    'F': 349.23,
    'G': 392.00,
    'A': 440.00,
    'B': 493.88
}

# De duur van elke noot (in seconden)
note_duration = 0.4

# De vrolijke melodie
melody = [
    'C', 'E', 'G', 'A', 'G', 'F', 'E', 'D', 'C', 'D', 'E', 'F', 'G', 'A', 'B',
    'E', 'G', 'B', 'C', 'B', 'A', 'G', 'F', 'E', 'F', 'G', 'A', 'B', 'C', 'D',
    'G', 'B', 'D', 'E', 'D', 'C', 'B', 'A', 'G', 'A', 'B', 'C', 'D', 'E', 'F',
    'A', 'C', 'E', 'F', 'E', 'D', 'C', 'B', 'A', 'B', 'C', 'D', 'E', 'F', 'G'
]

# Creëer de audio segmenten voor elke noot
audio = AudioSegment.silent(duration=0)
for note in melody:
    if note in notes_freq:
        frequency = notes_freq[note]
        audio += create_tone(frequency, note_duration)

# Speel de melodie af
play(audio)
