🎵 Shazam Clone – Song Recognition Web App
This is a Shazam-like web application where users can record audio or hum a tune and the system detects the song using ACRCloud Music Recognition API.

✨ Features

     🎤 Record Audio / Hum from the browser using MediaRecorder API
    
    🔄 Converts WebM → WAV using FFmpeg for API compatibility
    
    🎶 Song Recognition using ACRCloud Music Recognition API
    
    🌐 Deployed on Render with a publicly accessible link

🛠 Debug Logs implemented to verify:

    Audio uploaded successfully
    
    WAV conversion successful
    
    API responses received

🛠 Tech Stack

    Frontend: HTML, CSS, JavaScript (MediaRecorder API)
    
    Backend: Flask (Python)
    
    Audio Processing: FFmpeg
    
    Music Recognition: ACRCloud API
    
    Deployment: Render
    
    Version Control: GitHub

🚀 How It Works

1.User clicks Record → Mic audio is captured in WebM format

2.Backend converts audio to WAV using FFmpeg

3.ACRCloud API generates an audio fingerprint and matches it to songs

4.Song title & artist is returned and displayed on the website

🔗 Live Demo

Website: https://shazam-clone.onrender.com
