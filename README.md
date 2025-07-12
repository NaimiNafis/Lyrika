# Lyrika

A browser extension that listens to audio playing in any browser tab, identifies the song, and displays its lyrics, turning your browser into a smart, lyrics-aware music player.

## Project Structure

This project uses a client-server architecture:

1. **Browser Extension (Client)** - Written in JavaScript, captures audio from browser tabs
2. **Python Server (Backend)** - Processes audio and communicates with external APIs

```
lyrika/
├── extension/           # Browser extension (JavaScript)
│   ├── manifest.json
│   ├── popup.html
│   ├── offscreen.html   # For background processing
│   ├── css/
│   │   └── popup.css
│   ├── js/
│   │   ├── background.js
│   │   ├── popup.js
│   │   └── offscreen.js
│   ├── lib/
│   │   └── bootstrap/   # UI components
│   └── assets/
│       ├── icons/
│       ├── artist.png
│       ├── song-lyrics.png
│       └── youtube.png
│
├── server/              # Python backend
│   ├── app.py           # Flask application
│   ├── requirements.txt
│   ├── api/
│   │   ├── __init__.py
│   │   ├── acrcloud.py  # Song identification 
│   │   ├── genius.py    # Lyrics retrieval
│   │   └── gemini.py    # AI-powered lyrics and enhancements
│   └── README.md        # Server-specific documentation
│
└── README.md
```

## Features

- **One-Click Recognition**: Click the extension icon to start listening to the active tab's audio
- **Real-time Identification**: View "Listening..." status, then see Song Title and Artist upon successful match
- **Lyrics Display**: Full lyrics for the identified song appear in the popup
- **Copy to Clipboard**: Click the song title to copy "Song Title by Artist" to clipboard
- **Platform Links**: Open the song in YouTube, Spotify, and other music services
- **Translation**: Translate lyrics to various languages using Gemini AI
- **Similar Songs**: Get recommendations for similar songs based on the current track
- **Manual Search**: Option to manually search for lyrics if automatic identification fails
- **Graceful Error Handling**: Clear feedback for common edge-case scenarios

## Tech Stack

### Extension (Client)
- **Framework**: Plain JavaScript, HTML, CSS with Manifest V3
- **Audio Capture**: chrome.tabCapture API
- **UI Framework**: Bootstrap for responsive design
- **Communication**: Fetch API for server requests

### Server (Backend)
- **Framework**: Flask (Python)
- **Song Recognition**: ACRCloud API
- **Lyrics Source**: Genius API (with web scraping fallback)
- **AI Enhancement**: Google Gemini API
- **Security**: Environment variables for API keys

## Setup Instructions

### Server Setup
1. Navigate to the server directory: `cd server`
2. Create a virtual environment: `python -m venv venv`
3. Activate the environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Create a `.env` file with your API keys (see API Keys section)
6. Start the server: `python app.py`

### Extension Setup
1. In Chrome, go to `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked" and select the `extension` directory
4. Update the API_BASE_URL in `extension/js/background.js` if your server is not running on localhost:5000

## API Keys

You'll need to obtain API keys for:
1. **ACRCloud** - For song identification (14-day free trial available)
2. **Genius** - For lyrics retrieval
3. **Gemini** - For AI-powered lyrics, translation, and song meaning (optional)

Add these keys to the `.env` file in the server directory.

## Implementation Details

### Extension Flow
1. User clicks the extension icon and then "Identify Song"
2. Extension captures audio from the active tab
3. Audio is converted to base64 and sent to the server
4. Results are displayed in the extension popup

### Server Flow
1. Server receives audio data from the extension
2. Audio is processed and sent to ACRCloud for identification
3. Song metadata is used to search for lyrics on Genius
4. If Genius fails, Gemini API is used as a fallback for lyrics
5. Combined results are returned to the extension

## Enhanced Features

- **Lyrics Translation**: Translate lyrics to different languages using Google's Gemini API
- **Similar Song Recommendations**: Get AI-generated recommendations for similar songs
- **Song Meaning Analysis**: Understand the meaning behind song lyrics
- **Multiple Platform Links**: Open songs in various music streaming services
- **Fallback Systems**: If one API fails, the system tries alternative methods

## Edge Cases Handling

- **Instrumental Songs**: Display message "This appears to be an instrumental track"
- **Cover Versions**: Search for lyrics using just song title if artist-specific search fails
- **Background Noise**: Clear error messages with manual search option
- **API Failures**: Graceful error handling with multiple fallback options
- **Lyrics Validation**: Intelligent validation to ensure retrieved content is actually lyrics

## Development Notes

- Both components include mock data for development without API keys
- The server has built-in CORS support for local development
- The extension supports manual search as a fallback option
- Port conflicts: If port 5000 is in use (common on macOS with AirPlay), use PORT=5001 environment variable 