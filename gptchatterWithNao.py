import pygame
import os
from openai import OpenAI
import matplotlib.pyplot as plt
import sounddevice as sd
import numpy as np
import tempfile
from scipy.io import wavfile
from scipy.io.wavfile import write
from datetime import datetime, timezone, timedelta
import time
from pydub import AudioSegment
import matplotlib.animation as animation
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize
import warnings
import subprocess
import requests
import xml.etree.ElementTree as ET
import html
from bs4 import BeautifulSoup
import re
from icalendar import Calendar
import json
warnings.filterwarnings("ignore")
import random

import paho.mqtt.client as mqtt


# Define the MQTT server details
MQTT_BROKER = 'broker.emqx.io'  # Use the IP address or hostname of your MQTT broker
MQTT_PORT = 1883  # Default MQTT port is 1883 (use 8883 for SSL connections)
MQTT_TOPIC = 'NAO/SAY'
MQTT_MESSAGE = 'Hallo, Ik ben online!'

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    # Once connected, publish your message
    client.publish(MQTT_TOPIC, MQTT_MESSAGE)

def on_publish(client, userdata, mid):
    print("Message Published.")

client_id = f'python-mqtt-{random.randint(0, 1000)}'
nao = mqtt.Client(client_id)

# Assign event callbacks
nao.on_connect = on_connect
nao.on_publish = on_publish

# Connect to the MQTT broker
nao.connect(MQTT_BROKER, MQTT_PORT, 60)

# Initialiseer Pygame voor audio afspelen
pygame.mixer.init()

nao.publish(MQTT_TOPIC, MQTT_MESSAGE)

chatViaMic = False
speakWithNao = True

# Functie om de WAV af te spelen
def play_audio(file_path):
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

# Parameters
chunk_size = 1024  # Number of samples per frame


def getNewsContent(xmlContent) :

    # De XML-data laden
    root = ET.fromstring(xmlContent)

    returnContent =  "Het laatste nieuws op de Standaard.be van vandaag.\n"

    counter = 0

    # Door alle 'item' elementen heen lopen
    for item in root.findall('.//item'):
        counter = counter +1
        title = item.find('title').text
        # De 'description' tag bevat HTML-entiteiten, dus we converteren deze
        description = html.unescape(item.find('description').text)

        returnContent += "\n" + ". titel: " + str(title) + "\n" + "inhoud:"  + str(description)
        if (counter >=10) :
            continue
    
    print (returnContent)
    return returnContent


def get_weeks_start_and_end_dates(date):
    start = date - timedelta(days=date.weekday())  # Maandag
    end = start + timedelta(days=6)  # Zondag
    return start, end


def getPublicAgenda(url) :

    response = requests.get(url)
    calendar = Calendar.from_ical(response.content)
    
    returnContent = "Uw agenda inhoud: \n"

     # Haal de huidige datum op in UTC voor vergelijking
    today = datetime.now(timezone.utc).date()

   # Bepaal de start- en einddatum van de huidige week
    today = datetime.now(timezone.utc).date()
    week_start, week_end = get_weeks_start_and_end_dates(today)      
    
    print (today)
    
    events = [] 


    for component in calendar.walk():
        if component.name == "VEVENT":
            summary = component.get('summary')
            dtstart = component.get('dtstart')
            dtend = component.get('dtend')
            location = component.get('location')

            # Controleer of summary en location bestaan voordat to_ical wordt aangeroepen
            summary = summary.to_ical().decode('utf-8') if summary else 'Geen samenvatting opgegeven'
            location = location.to_ical().decode('utf-8') if location else 'Geen locatie opgegeven'

            # Filter op evenementen van deze week (optioneel)
            if ((str(dtstart.dt)[:10] == str(today)[:10])):
                if (dtend is not None and dtstart is not None and len(summary)>5) :
                    events.append({
                        "summary": summary,
                        "start": str(dtstart.dt)[:16],
                        "end": str(dtend.dt)[:16],
                        "location": location
                    })
    json_str = json.dumps(events)
    print (json_str)
    return json_str


# Functie om icalendar date/datetime objecten naar Python datetime/date te converteren
def convert_to_python_datetime(ical_datetime):
    if (ical_datetime is None) :
        return ""
    else :
        if isinstance(ical_datetime.dt, datetime):
            # Als het een datetime is, zet om naar de juiste tijdzone (indien nodig)
            return ical_datetime.dt.astimezone(timezone.utc)
    print (ical_datetime.dt)
    return ical_datetime.dt




def rms(frame):
    """
    Bereken de root mean square van de audio frame.
    """
    return np.sqrt(np.mean(np.square(frame), axis=0))

def record_until_silence(threshold=0.015, fs=44100, chunk_size=1024, max_silence=5):
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
    silent_frames = 5
    silence_limit = int(max_silence * fs / chunk_size)  # Aantal frames van stilte voordat opname stopt
    recording_started = False

    def callback(indata, frames, time, status):
        nonlocal silent_frames, recording_started
        volume_norm = rms(indata)
        if volume_norm < threshold:
            silent_frames += 1
            if silent_frames > silence_limit:
                raise sd.CallbackStop
        else:
            silent_frames = 0
            recording_started =  True
        
        recorded_frames.append(indata.copy())

    with sd.InputStream(callback=callback, device=1, dtype='float32', channels=1, samplerate=fs, blocksize=chunk_size):
        print("Opname gestart. Wacht op geluid...")
        sd.sleep(5000)  # Wacht maximaal 10 seconden voor geluid


    if (recording_started == False ) :
        print("\nGeen vraag waargenomen.")
        return 0
    else:
        print("Einde van de opname. Even geduld aub.")
        recording = np.concatenate(recorded_frames, axis=0)
        # Tijdelijk bestand aanmaken en opname opslaan
        temp_file = tempfile.mktemp(prefix='opgenomen_audio_', suffix='.wav')
        write(temp_file, fs, recording)  # Schrijf de opname naar een WAV-bestand

        #print(f"Audio opgenomen en opgeslagen in: {temp_file}")
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

firstCall = True
start_time = time.perf_counter()  # Precieze starttijd
toWait = 0

while True:
    # Ask user for input
    # Opname starten

    if (firstCall != True) :

        if (chatViaMic == False) :
            user_input = input("Your message: ")
        else :

            audio_file_path = record_until_silence()
            
            
            if (audio_file_path == 0) :
                continue


            #start_time = time.perf_counter()  # Precieze starttijd
            #subprocess.Popen(['python', 'playmp3.py', 'waiting\zeerLangWachten.mp3'])
            #toWait = 5


            with open(audio_file_path, "rb") as audio_file:
                user_input = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file
                )
            # Check if the user wants to exit the chat
            user_input = user_input.text
            

    else :
        firstCall = False
        user_input = "Hallo wie ben jij?"


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

            start_time = time.perf_counter()  # Precieze starttijd
            subprocess.Popen(['python', 'playmp3.py', 'waiting\weeropzoeken.mp3'])
            toWait = 5

            response = requests.get('https://www.meteo.be/nl/weer/verwachtingen/weer-voor-de-komende-dagen')
            if response.status_code == 200:
                # Gebruik BeautifulSoup om de HTML te parsen
                soup = BeautifulSoup(response.text, 'lxml')
                # Extract de tekst zonder HTML tags
                text = soup.get_text()
                gevonden_tekst = re.search(r'Laatste update:(.*?)Uitleg over onze voorspellingen', text, re.DOTALL)
                inhoud =  gevonden_tekst.group(1).strip()
                messages.append({"role": "assistant", "content": inhoud})  # Corrected line

    words_to_test = ['laatste nieuws']
    # Perform the test
    for word in words_to_test:
        if word.lower() in user_input.lower():
            start_time = time.perf_counter()  # Precieze starttijd
            subprocess.Popen(['python', 'playmp3.py', 'waiting\standaardopzoeken.mp3'])
            toWait = 7
            response = requests.get('https://www.standaard.be/rss/section/1f2838d4-99ea-49f0-9102-138784c7ea7c')
            inhoud = getNewsContent (response.text)
            if response.status_code == 200:
                # De tekst van de webpagina opslaan in een variabele
                webpagina_tekst = inhoud
                messages.append({"role": "assistant", "content": webpagina_tekst})  # Corrected line

    words_to_test = ['agenda']
    for word in words_to_test:
        if word.lower() in user_input.lower():
            start_time = time.perf_counter()  # Precieze starttijd
            subprocess.Popen(['python', 'playmp3.py', 'waiting\/agenda.mp3'])
            toWait = 7
            response = getPublicAgenda('https://calendar.google.com/calendar/ical/maarten.dequanter%40gmail.com/private-011d782da2fa4134d76a95411500c373/basic.ics')
            messages.append({"role": "assistant", "content": response})  # Corrected line




    messages.append({"role": "assistant", "content": user_input}) 

    # Plaats hier de code waarvan je de uitvoeringstijd wilt meten

    # Generate a response from the model
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    end_time = time.perf_counter()  # Precieze eindtijd
    total_time = end_time - start_time


    print(f"Totale uitvoeringstijd voor chat: {total_time} seconden.")

    start = time.time()

    # current date and time
    date_time = datetime.now()

    # format specification
    format = '%Y%m%d%H%M%S'

    # applying strftime() to format the datetime
    string = date_time.strftime(format)

    start_time = time.perf_counter()  # Precieze starttijd
    # Plaats hier de code waarvan je de uitvoeringstijd wilt meten

    if (speakWithNao == False) :

        speech_file_path = 'speech' + str(string)+ ".mp3"
        response = client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=completion.choices[0].message.content
        )

        end_time = time.perf_counter()  # Precieze eindtijd
        total_time = end_time - start_time
        while (total_time < toWait) :
            time.sleep(0.5)
            end_time = time.perf_counter()  # Precieze eindtijd
            total_time = end_time - start_time
        
        print(f"Totale uitvoeringstijd voor speech: {total_time} seconden.")


        response.stream_to_file(speech_file_path)
        end = time.time()

        calc_time = end
        #print (calc_time)


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
                #fft_data_filtered = fft_data[(x >= 80) & (x <= 2600)]
                for bar, height in zip(bars, fft_data):
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
    else :
        nao.publish(MQTT_TOPIC, completion.choices[0].message.content)
    
    # Add model's response to the messages list to maintain context
    messages.append({"role": "assistant", "content": completion.choices[0].message.content})  # Corrected line

    while (messageEnded != True):
        nao.loop_start() #start the loop
        time.sleep(1000)
        print ("looking for mqtt end")
        client.loop_stop() #stop the loop


