# app.py
from flask import Flask, request, jsonify, render_template
import requests
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Audd.io API endpoint for song recognition
AUDD_API_URL = "https://api.audd.io/"

# TODO: Replace with your actual Audd.io API key
# Get your free API key at https://audd.io/
AUDD_API_KEY = "c959a75808e0a1d3c30b6094059820d1"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/identify', methods=['POST'])
def identify_song():
    try:
        # Check if audio file is in the request
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        
        if audio_file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        # Validate file type (basic validation)
        filename = secure_filename(audio_file.filename)
        if not filename.lower().endswith(('.webm', '.wav', '.mp3', '.ogg')):
            return jsonify({'error': 'Unsupported file format. Please use webm, wav, mp3, or ogg'}), 400
        
        # Prepare the data for Audd.io API
        files = {
            'file': (filename, audio_file.stream, audio_file.content_type)
        }
        
        # Data for the API request
        # TODO: Replace 'your_api_key_here' with your actual Audd.io API key
        data = {
            'api_token': AUDD_API_KEY,  # Replace with your actual API key
            'return': 'title,artist'  # Specify what information to return
        }
        
        # Send request to Audd.io API
        response = requests.post(AUDD_API_URL, data=data, files=files, timeout=30)
        
        # Check if the request was successful
        if response.status_code != 200:
            return jsonify({'error': f'API request failed with status {response.status_code}'}), 500
        
        # Parse the JSON response from Audd.io
        api_response = response.json()
        
        # Check if the song was identified
        if api_response.get('status') == 'success' and api_response.get('result'):
            result = api_response['result']
            return jsonify({
                'title': result.get('title', 'Unknown'),
                'artist': result.get('artist', 'Unknown Artist')
            })
        else:
            # Song not identified
            return jsonify({'title': None, 'artist': None})
            
    except requests.exceptions.RequestException as e:
        # Network or request error
        return jsonify({'error': f'Network error: {str(e)}'}), 500
    except Exception as e:
        # Other errors
        return jsonify({'error': f'Server error: {str(e)}'}), 500

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)