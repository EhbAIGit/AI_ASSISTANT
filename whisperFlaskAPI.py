from flask import Flask, request, jsonify
import os
import whisper

app = Flask(__name__)

# Load Whisper model
model = whisper.load_model("base")

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    
    audio_file = request.files['file']
    
    if audio_file.filename == '':
        return jsonify({'error': 'No selected file'})
    
    allowed_extensions = {'.mp3', '.wav'}
    file_extension = os.path.splitext(audio_file.filename)[1].lower()
    
    if file_extension not in allowed_extensions:
        return jsonify({'error': 'Invalid file format. Only MP3 and WAV files are supported.'})
    
    try:
        # Save the audio file temporarily
        audio_file_path = 'temp_audio' + file_extension
        audio_file.save(audio_file_path)
        
        # Transcribe the audio using Whisper
        result = model.transcribe(audio_file_path)
        
        # Return the transcribed text
        return jsonify({'text': result['text']})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
