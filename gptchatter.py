import pygame
from openai import OpenAI
import sounddevice as sd
import numpy as np
import tempfile
from scipy.io.wavfile import write
from datetime import datetime
import time




def play_mp3(file_path):
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()


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
with open('context.txt', 'r') as file:
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
    input("Druk op Enter om verder te gaan")

    
    audio_file_path = record_until_silence()

    #user_input = input("Your message: ")
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
        model="gpt-3.5-turbo",
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


    play_mp3(speech_file_path)
    # Houd het programma actief totdat de muziek eindigt
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)   
    
    # Print the model's response
    print("NAO:", completion.choices[0].message.content)  # Corrected line
    
    # Add model's response to the messages list to maintain context
    messages.append({"role": "assistant", "content": completion.choices[0].message.content})  # Corrected line
