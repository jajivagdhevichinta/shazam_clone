from flask import Flask, request, jsonify, render_template
import os, sys, hmac, hashlib, base64, time, requests
from werkzeug.utils import secure_filename

sys.stdout.reconfigure(line_buffering=True)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Replace with your ACRCloud credentials
HOST = "identify-ap-southeast-1.acrcloud.com"
ACCESS_KEY = "b7cc485c54c21f3313743ed19697ec14"
ACCESS_SECRET = "WgEB1VRVuYV9zF4l8i8VVNyGeNebD4XwdnWWoPBU"

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
        audio_file.save(input_path)
        file_size = os.path.getsize(input_path)
        print("DEBUG: Input file size:", file_size, "bytes", flush=True)

        # Prepare ACRCloud signature
        http_method = "POST"
        http_uri = "/v1/identify"
        data_type = "audio"
        signature_version = "1"
        timestamp = str(int(time.time()))

        string_to_sign = "\n".join([http_method, http_uri, ACCESS_KEY, data_type, signature_version, timestamp])
        sign = base64.b64encode(
            hmac.new(ACCESS_SECRET.encode('utf-8'), string_to_sign.encode('utf-8'), digestmod=hashlib.sha1).digest()
        ).decode('utf-8')

        # Send file to ACRCloud
        files = {'sample': open(input_path, 'rb')}
        data = {
            'access_key': ACCESS_KEY,
            'data_type': data_type,
            'signature_version': signature_version,
            'signature': sign,
            'sample_bytes': file_size,
            'timestamp': timestamp,
        }

        response = requests.post(f"http://{HOST}/v1/identify", files=files, data=data, timeout=30)
        print("DEBUG: ACRCloud raw response:", response.text, flush=True)

        os.remove(input_path)

        if response.status_code != 200:
            return jsonify({'error': f'API request failed with status {response.status_code}'}), 500

        result = response.json()
        if result.get('status', {}).get('code') == 0:
            music = result.get('metadata', {}).get('music', [])
            if music:
                song = music[0]
                return jsonify({'title': song.get('title', 'Unknown'),
                                'artist': song.get('artists', [{}])[0].get('name', 'Unknown Artist')})
        return jsonify({'title': None, 'artist': None})

    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
