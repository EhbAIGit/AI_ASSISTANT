import pygame
from openai import OpenAI
import matplotlib.pyplot as plt
import sounddevice as sd
import numpy as np
import tempfile
from scipy.io import wavfile
from scipy.io.wavfile import write
from datetime import datetime
import time
from pydub import AudioSegment
import matplotlib.animation as animation
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize


# Initialiseer Pygame voor audio afspelen
pygame.mixer.init()

# Functie om de WAV af te spelen
def play_audio(file_path):
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

# Parameters
chunk_size = 1024  # Number of samples per frame

def rms(frame):
    """
    Bereken de root mean square van de audio frame.
    """
    return np.sqrt(np.mean(np.square(frame), axis=0))

def record_until_silence(threshold=0.01, fs=44100, chunk_size=1024, max_silence=5):
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
        sd.sleep(5000)  # Wacht maximaal 10 seconden voor geluid


    print("\nEinde van de opname.")
    recording = np.concatenate(recorded_frames, axis=0)

    # Tijdelijk bestand aanmaken en opname opslaan
    temp_file = tempfile.mktemp(prefix='opgenomen_audio_', suffix='.wav')
    write(temp_file, fs, recording)  # Schrijf de opname naar een WAV-bestand

    print(f"Audio opgenomen en opgeslagen in: {temp_file}")
    return temp_file


client = OpenAI()

# Initial system message to set the context for the chat

# Open het tekstbestand in leesmodus ('r')
with open('filters.txt', 'r') as file:
    print ("Filters gelezen")
    # Lees de inhoud van het bestand en sla het op in een string
    inhoud = file.read()



initial_messages = [
    {"role": "system", "content": inhoud},
]

# Initialize messages list with the initial system message
messages = initial_messages.copy()

while True:
    # Ask user for input
    # Opname starten
    

    #user_input = input("Your message: ")
    
    input("Druk op Enter om verder te gaan")
    audio_file_path = record_until_silence()
    with open(audio_file_path, "rb") as audio_file:
        user_input = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_file
        )
    
    
    # Check if the user wants to exit the chat
    user_input = user_input.text
    
    #user_input = input("Your message:")
    

    if user_input.lower() == 'exit':
        print("Exiting chat...")
        break
    
    # Define the words to test for
    words_to_test = ['kenniscentra', 'onderzoek']

    # Perform the test
    for word in words_to_test:
        if word.lower() in user_input.lower():
            messages.append({"role": "assistant", "content": "Erasmushogeschool heeft onderzoekscentra. Namelijk Kenniscentrum Artificial Intelligence,  Kenniscentrum BruChi, Kenniscentrum Open BioLab Brussels, Kenniscentrum OpenTime, Kenniscentrum PAKT, Kenniscentrum Urban Coaching & Education, Kenniscentrum Tuin+"})  # Corrected line
 
    # Define the words to test for
    words_to_test = ['weerbericht']
    # Perform the test
    for word in words_to_test:
        if word.lower() in user_input.lower():
            messages.append({"role": "assistant", "content": "Zeg dat je het weerbericht via  een API kan ophalen en vraag naar de locatie. Eens je de locatie weet maak je een json string van de vorm  {\"actionname\"': \"weather\",\"location\": \"gevraagde\"}"})  # Corrected line



    # Add user message to the messages list
    messages.append({"role": "user", "content": user_input})
    
    # Generate a response from the model
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )


    start = time.time()

    # current date and time
    date_time = datetime.now()

    # format specification
    format = '%Y%m%d%H%M%S'

    # applying strftime() to format the datetime
    string = date_time.strftime(format)


    speech_file_path = 'speech' + str(string)+ ".mp3"
    response = client.audio.speech.create(
    model="tts-1-hd",
    voice="nova",
    input=completion.choices[0].message.content
    )


    response.stream_to_file(speech_file_path)
    end = time.time()

    calc_time = end
    print (calc_time)


    # Laden van het MP3-bestand
    mp3File = speech_file_path
    audio = AudioSegment.from_mp3(mp3File)
    # Exporteren naar WAV
    pygame.mixer.quit()
    audio.export('vumeter.wav', format="wav")
    pygame.mixer.init()


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
    
    # Print the model's response
    print("NAO:", completion.choices[0].message.content)  # Corrected line
    
    # Add model's response to the messages list to maintain context
    messages.append({"role": "assistant", "content": completion.choices[0].message.content})  # Corrected line
