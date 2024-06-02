from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import time
import io
from gtts import gTTS  # Google Text-to-Speech
import pyttsx3


def text_to_speech(text, filename, voice_id=None):
    engine = pyttsx3.init()
    if voice_id:
        engine.setProperty('voice', voice_id)
    engine.save_to_file(text, filename)
    engine.runAndWait()

app = Flask(__name__)
UPLOAD_FOLDER = 'google/uploads'
RESPONSE_FOLDER = 'google/responses'
RESPONSE_FILE = "d:\\Github\\AI_ASSISTANT\\google\\responses\\response_newest.mp3"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESPONSE_FOLDER'] = RESPONSE_FOLDER
app.config['RESPONSE_FILE'] = RESPONSE_FILE

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(RESPONSE_FOLDER):
    os.makedirs(RESPONSE_FOLDER)

@app.route('/')
def index():
    return render_template('indexVoice.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'audio_data' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['audio_data']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    now = datetime.now()
    formatted_string = now.strftime("%Y%m%d%H%M%S")
    filename = formatted_string + "_" + secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)


    '''
    Add ChatGPT code here
    '''



    # Generate a response audio
    formatted_string_saved = now.strftime("%H %M %S")
    response_text = "Hello! You have reached our automated answering machine. We have successfully recorded your message at " + now.strftime("%H:%M:%S") + ". ""Thank you for getting in touch with us. We will get back to you shortly. ""Have a great day!"
    # tts = gTTS(text=response_text, lang='en')
    #response_text = ("Hallo! U heeft ons automatische antwoordapparaat bereikt. "
    #             "We hebben uw bericht succesvol opgenomen om " + now.strftime("%H:%M:%S") + ". "
    #             "Bedankt voor uw bericht. We nemen binnenkort contact met u op. "
    #             "Fijne dag verder!")
    # tts = gTTS(text=response_text, lang='nl', slow=False)   
    

    
    response_filename = formatted_string + "_response.mp3"
    response_filename = "response_newest" + now.strftime("%H%M%S") + ".mp3"
    response_filepath = os.path.join(app.config['RESPONSE_FOLDER'], response_filename)
    
    # tts.save(response_filepath)
    response_filepath = os.path.join(app.config['RESPONSE_FOLDER'], response_filename)

    # Set the voice ID (replace 'voice_id' with the actual ID you want to use)
    voice_id = "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0"  # Example for macOS

    text_to_speech(response_text, response_filepath, voice_id)

    app.config['RESPONSE_FILE'] = "d:\\Github\\AI_ASSISTANT\\google\\responses\\" + response_filename

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return jsonify({"success": True, "filepath": filepath, "response_filepath": response_filepath + "?" + timestamp}), 200

@app.route('/responses/<filename>')
def get_response(filename):
    return send_file(app.config['RESPONSE_FILE'], mimetype='audio/mp3')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
