from pathlib import Path
from openai import OpenAI
from datetime import datetime
client = OpenAI()
import time

start = time.time()

# current date and time
date_time = datetime.now()

# format specification
format = '%Y%m%d%H%M%S'

# applying strftime() to format the datetime
string = date_time.strftime(format)


with open('tts_tekst.txt', 'r') as file:
    # Lees de inhoud van het bestand en sla het op in een string
    inhoud = file.read()


inhoud = "OK,  Ik kijk de agenda even na. Even geduld alsjeblieft."

speech_file_path = 'speech' + str(string)+ ".mp3"
response = client.audio.speech.create(
  model="tts-1",
  voice="nova",
  input=inhoud
)


response.stream_to_file(speech_file_path)
end = time.time()

calc_time = end
print (calc_time)