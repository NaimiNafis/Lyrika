# Lyrika Browser Extension

Browser extension that captures audio from browser tabs, sends it to the Lyrika server for identification, and displays song lyrics.

## Features

- Audio capture from any browser tab
- Song identification with metadata display
- Full lyrics display
- YouTube links for identified songs
- Manual search option for fallback

## Setup

1. Make sure the Lyrika server is running first
2. Update the API_BASE_URL in `js/background.js` if your server is not running on localhost:5000
3. Load the extension in Chrome:
   - Go to `chrome://extensions/`
   - Enable "Developer mode"
   - Click "Load unpacked" and select this directory

## File Structure

- `manifest.json`: Extension configuration
- `popup.html`: Main extension UI
- `css/popup.css`: Styling for the UI
- `js/background.js`: Background script handling audio capture and API communication
- `js/popup.js`: UI interactions and state management
- `assets/icons/`: Extension icons

## Audio Processing

The extension uses the following steps to process audio:

1. Captures audio stream from the active tab using chrome.tabCapture API
2. Creates a MediaRecorder to record audio in webm format
3. Records for 10 seconds
4. Converts the audio data to base64
5. Sends the base64 data to the Lyrika server for processing

## User Interface States

The extension UI has four main states:

1. **Initial State**: Shows the "Identify Song" button
2. **Listening State**: Shows an animation while recording audio
3. **Results State**: Displays song info, lyrics, and YouTube link
4. **Error State**: Shows error message and try again button

## Manual Search

If automatic song identification fails, users can:

1. Enter song title and artist manually
2. Click "Search Lyrics" to perform a manual search
3. View lyrics from the manual search result

## Development

For development without a running server, the extension includes mock responses. To test with the actual server:

1. Start the Lyrika server
2. Comment out the `return await mockServerResponse();` line in `background.js`
3. The extension will then make actual API calls to the server 