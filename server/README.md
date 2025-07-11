# Lyrika Server

Python Flask server that processes audio data from the Lyrika browser extension, identifies songs, and retrieves lyrics.

## Setup

1. Create a virtual environment:
   ```
   python -m venv venv
   ```

2. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```
   cp env.sample .env
   ```
   Then edit `.env` and add your API keys.

5. Start the server:
   ```
   python app.py
   ```
   The server will run at http://localhost:5000

## API Endpoints

### GET /api/health
Health check endpoint to verify the server is running.

**Response:**
```json
{
  "status": "success",
  "message": "Lyrika API is running"
}
```

### POST /api/identify
Identifies a song from audio data and fetches its lyrics.

**Request:**
```json
{
  "audio_data": "base64_encoded_audio_data"
}
```

**Response:**
```json
{
  "status": "success",
  "title": "Bohemian Rhapsody",
  "artist": "Queen",
  "lyrics": "Is this the real life? Is this just fantasy?...",
  "youtubeId": "fJ9rUzIMcZQ"
}
```

### GET /api/lyrics?title=TITLE&artist=ARTIST
Gets lyrics for a song by title and artist.

**Query Parameters:**
- `title` (required): Song title
- `artist` (optional): Artist name

**Response:**
```json
{
  "status": "success",
  "title": "Bohemian Rhapsody",
  "artist": "Queen",
  "lyrics": "Is this the real life? Is this just fantasy?...",
  "source_url": "https://genius.com/Queen-bohemian-rhapsody-lyrics"
}
```

## Required API Keys

1. **ACRCloud** - For song identification
   - Sign up at [ACRCloud](https://www.acrcloud.com/)
   - Create a project with the "Music Recognition" type
   - Copy Host, Access Key, and Access Secret to your `.env` file

2. **Genius API** - For lyrics retrieval
   - Sign up at [Genius API](https://genius.com/api-clients)
   - Create an API client
   - Copy Client Access Token to your `.env` file

## Development

The server includes mock implementations for both ACRCloud and Genius APIs for development without API keys. These mock implementations will be used automatically if no API keys are provided. 