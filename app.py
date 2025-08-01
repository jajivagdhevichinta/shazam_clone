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
        print("Input file size:", os.path.getsize(input_path), "bytes")

        # Convert to WAV
        subprocess.run(['ffmpeg', '-i', input_path, output_path, '-y'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if os.path.exists(output_path):
            print("Output WAV size:", os.path.getsize(output_path), "bytes")
        else:
            print("Output WAV not created")

        # Send WAV to Audd.io
        with open(output_path, 'rb') as f:
            data = {'api_token': AUDD_API_KEY, 'return': 'title,artist'}
            response = requests.post(AUDD_API_URL, data=data, files={'file': f}, timeout=30)

        # Print raw API response
        print("Audd.io raw response:", response.text)

        # Cleanup
        os.remove(input_path)
        os.remove(output_path)

        # Return result
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
