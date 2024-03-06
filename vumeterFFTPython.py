import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt

# Parameters
fs = 44100  # Sample rate
chunk_size = 1024  # Number of samples per frame

# Configureer de plot voor live-updating
fig, ax = plt.subplots()
x_fft = np.linspace(0, fs // 2, chunk_size // 2)
line, = ax.plot(x_fft, np.zeros(chunk_size // 2))
ax.set_xlim(20, fs // 2)
ax.set_ylim(0, 100)  # Pas de y-aslimiet aan op basis van je behoeften
ax.set_xlabel('Frequency (Hz)')
ax.set_ylabel('Magnitude')
ax.set_title('Realtime Frequency Spectrum')

# Functie om de plot te updaten
def update_plot():
    data, _ = sd.rec(chunk_size, samplerate=fs, channels=1, dtype='float32', blocking=True)
    data = data.flatten()
    fft_data = np.fft.rfft(data)
    magnitude = np.abs(fft_data) / chunk_size
    line.set_ydata(magnitude)
    fig.canvas.draw()
    fig.canvas.flush_events()

# InputStream instellen (vervang 'device=1' door het juiste apparaat-ID indien nodig)
stream = sd.InputStream(device=1, channels=1, samplerate=fs, blocksize=chunk_size, dtype='float32')

# Start de stream en de loop voor het updaten van de plot
with stream:
    plt.ion()  # Zet de interactieve modus aan
    while True:  # Vervang True door een geschikte conditie als je een stopconditie wilt
        update_plot()
        plt.pause(0.05)  # Korte pauze om de GUI te updaten en niet de CPU te overbelasten

# Optioneel: voeg een manier toe om de loop te breken, bijvoorbeeld door een toetsaanslag te detecteren
