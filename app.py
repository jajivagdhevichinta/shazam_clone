from flask import Flask, request, jsonify, render_template
import requests, os, subprocess
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

AUDD_API_URL = "https://api.audd.io/"
AUDD_API_KEY = "c959a75808e0a1d3c30b6094059820d1"  # Replace with your real key

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/identify', methods=['POST'])
def identify_song():
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400

        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        filename = secure_filename(audio_file.filename)
        input_path = f"temp_input.{filename.split('.')[-1]}"
        output_path = "temp_output.wav"

        # Save uploaded file
        audio_file.save(input_path)

        # Convert to WAV using ffmpeg
        subprocess.run(['ffmpeg', '-i', input_path, output_path, '-y'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Send WAV file to Audd.io
        with open(output_path, 'rb') as f:
            data = {'api_token': AUDD_API_KEY, 'return': 'title,artist'}
            response = requests.post(AUDD_API_URL, data=data, files={'file': f}, timeout=30)

        # Cleanup temp files
        os.remove(input_path)
        os.remove(output_path)

        # Process API response
        if response.status_code != 200:
            return jsonify({'error': f'API request failed with status {response.status_code}'}), 500

        api_response = response.json()
        if api_response.get('status') == 'success' and api_response.get('result'):
            result = api_response['result']
            return jsonify({'title': result.get('title', 'Unknown'), 'artist': result.get('artist', 'Unknown Artist')})
        else:
            return jsonify({'title': None, 'artist': None})

    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
