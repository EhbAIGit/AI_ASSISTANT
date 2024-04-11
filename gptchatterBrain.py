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
import serial
import keyboard



# Seriële poort instellen
ser = serial.Serial('COM7', 9600)  # Vervang 'COM1' door de juiste poort en 9600 door de juiste baudrate

bericht = "pftpftpftpftpft"
ser.write(bericht.encode()) 
 

messageEnded = True

# Initialiseer Pygame voor audio afspelen
pygame.mixer.init()

chatViaMic = True


def get_audio_length(file_path):
    audio = AudioSegment.from_mp3(file_path)
    return len(audio)  # De lengte van het audiobestand in seconden



# Functie om de WAV af te spelen
def play_audio(file_path):
    length_seconds = get_audio_length(file_path)/200
    command = "pf" * int(length_seconds)
    ser.write(command.encode()) 
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
        if keyboard.is_pressed('space'):
            return(True)  


    with sd.InputStream(callback=callback, device=1, dtype='float32', channels=1, samplerate=fs, blocksize=chunk_size):
        print("Opname gestart. Wacht op geluid...")
        bericht = "tttttttttttttttttttttttttttttttttttttttttttt"
        ser.write(bericht.encode()) 
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
with open('contextBrain.txt', 'r') as file:
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
            print("Druk op de spatiebalk om te beginnen met opnemen.")
            while (True) :
                if keyboard.is_pressed('space'):
                    break   

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

    # Start audio playback
    play_audio(audio_file_path)


    
    # Print the model's response
    print("ROBOT:", completion.choices[0].message.content)  # Corrected line
    
    # Add model's response to the messages list to maintain context
    messages.append({"role": "assistant", "content": completion.choices[0].message.content})  # Corrected line