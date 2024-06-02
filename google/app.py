from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = 'google/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

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
    #print (filepath)
    return jsonify({"success": True, "filepath": filepath}), 200

if __name__ == '__main__':
   app.run(host='0.0.0.0', port=5000, debug=True)
