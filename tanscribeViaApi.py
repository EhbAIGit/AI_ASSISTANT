import requests

# Define the URL of the Flask server
url = 'http://127.0.0.1:8089/transcribe'  # Update with your Flask server's URL

# Path to the MP3 file you want to send
file_path = "speech/opgenomen_audio_70b6lrme.wav"  # Update with the path to your MP3 file

# Create a dictionary containing the file to be sent
files = {'file': open(file_path, 'rb')}

# Send the POST request
try:
    response = requests.post(url, files=files)
    
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Print the transcribed text
        print("Transcribed Text:")
        print(response.json()['text'])
    else:
        print(f"Error: {response.status_code} - {response.reason}")
except Exception as e:
    print(f"Error: {e}")