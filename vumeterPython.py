import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize

# Parameters
fs = 5000  # Sample rate
duration = 10  # seconds
chunk_size = 512  # Number of samples per frame

# Start the stream
stream = sd.InputStream(device=1, channels=1, samplerate=fs, blocksize=chunk_size, dtype='float32')
stream.start()

fig, ax = plt.subplots()
x = np.fft.rfftfreq(chunk_size, 1/fs)
x_filtered = x[(x >= 80) & (x <= 2600)]
bars = ax.bar(x_filtered, np.zeros_like(x_filtered), width=np.diff(x_filtered)[0])

# Creëer een colormap van groen naar rood
cmap = plt.get_cmap('RdYlGn_r')  # '_r' om de volgorde om te draaien
norm = Normalize(vmin=-2, vmax=2)  # Aanpassen op basis van je data
sm = ScalarMappable(norm=norm, cmap=cmap)

def init():
    ax.set_xlim(80, 2600)  # Beperk de x-as tot het bereik van menselijke spraak
    ax.set_ylim(0, 2)  # Stel een geschikte y-as limiet in
    return bars

def update(frame):
    data, _ = stream.read(chunk_size)
    fft_data = np.abs(np.fft.rfft(data.flatten()))
    fft_data_filtered = fft_data[(x >= 80) & (x <= 2600)]
    for bar, height in zip(bars, fft_data_filtered):
        bar.set_height(height)
        bar.set_color(cmap(norm(height)))  # Update de kleur gebaseerd op de hoogte
    return bars

ani = animation.FuncAnimation(fig, update, init_func=init, blit=False, interval=10)

plt.show()
