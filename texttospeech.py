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


speech_file_path = 'speech' + str(string)+ ".mp3"
response = client.audio.speech.create(
  model="tts-1",
  voice="alloy",
  input="Hello everyone, I am NAO, a humanoid robot, a marvel of robotics and artificial intelligence. Crafted with the precision of advanced technology, my existence bridges the gap between human imagination and reality."
)


response.stream_to_file(speech_file_path)
end = time.time()

calc_time = end
print (calc_time)