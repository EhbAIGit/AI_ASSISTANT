import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize
import pygame
from scipy.io import wavfile
from pydub import AudioSegment

# Initialiseer Pygame voor audio afspelen
pygame.mixer.init()

# Functie om de WAV af te spelen
def play_audio(file_path):
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

# Parameters
chunk_size = 1024  # Number of samples per frame

# Laad WAV-bestand

# Laden van het MP3-bestand
mp3File = 'speech20240222132403.mp3'
audio = AudioSegment.from_mp3(mp3File)
# Exporteren naar WAV
audio.export('vumeter.wav', format="wav")


audio_file_path = 'vumeter.wav'  # Vervang dit door het pad naar je WAV-bestand
samplerate, data = wavfile.read(audio_file_path)
if data.ndim > 1:
    data = np.mean(data, axis=1)  # Converteer naar mono indien nodig

# Bereken de totale afspeelduur in milliseconden
total_duration_ms = 1000 * len(data) / samplerate

fig, ax = plt.subplots()
x = np.fft.rfftfreq(chunk_size, 1/samplerate)
x_filtered = x[(x >= 80) & (x <= 2600)]
bars = ax.bar(x_filtered, np.zeros_like(x_filtered), width=np.diff(x_filtered)[0])

# Creëer een colormap van groen naar rood
cmap = plt.get_cmap('RdYlGn_r')
norm = Normalize(vmin=0, vmax=1000000)
sm = ScalarMappable(norm=norm, cmap=cmap)

def init():
    ax.set_xlim(80, 2600)
    ax.set_ylim(0, 1000000)
    return bars

def update(frame):
    current_pos_ms = pygame.mixer.music.get_pos()
    if current_pos_ms == -1:  # Check of de muziek is gestopt
        ani.event_source.stop()  # Stop de animatie
        plt.close(fig)  # Sluit de plot
        return bars
    current_sample_index = int(current_pos_ms * samplerate / 1000)
    start = max(0, current_sample_index - chunk_size // 2)
    end = min(len(data), start + chunk_size)
    if end <= len(data):
        fft_data = np.abs(np.fft.rfft(data[start:end]))
        fft_data_filtered = fft_data[(x >= 80) & (x <= 2600)]
        for bar, height in zip(bars, fft_data_filtered):
            bar.set_height(height)
            bar.set_color(cmap(norm(height)))
    return bars

# Start audio playback
play_audio(audio_file_path)

# Start de animatie
ani = animation.FuncAnimation(fig, update, init_func=init, blit=False, interval=50)

plt.show()
