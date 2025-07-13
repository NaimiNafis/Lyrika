# Lyrika Browser Extension

Browser extension that captures audio from browser tabs, sends it to the Lyrika server for identification, and displays song lyrics.

## Features

- Audio capture from any browser tab
- Song identification with metadata display
- Full lyrics display
- YouTube and Spotify links for identified songs
- Manual search option for fallback
- Lyrics translation to multiple languages
- Similar songs recommendations
- Song meaning analysis
- Copy song info to clipboard

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
- `offscreen.html`: Background processing page for audio capture
- `css/popup.css`: Styling for the UI
- `js/background.js`: Background script handling audio capture and API communication
- `js/popup.js`: UI interactions and state management
- `js/offscreen.js`: Offscreen document handling for audio processing
- `assets/`: Icons and images for the extension

## Audio Processing

The extension uses the following steps to process audio:

1. Captures audio stream from the active tab using chrome.tabCapture API
2. Creates a MediaRecorder to record audio in webm format
3. Records for 10 seconds
4. Converts the audio data to base64
5. Sends the base64 data to the Lyrika server for processing

## User Interface States

The extension UI has multiple states:

1. **Initial State**: Shows the "Identify Song" button
2. **Listening State**: Shows an animation while recording audio
3. **Results State**: Displays song info, lyrics, and platform links
4. **Error State**: Shows error message and try again button
5. **Translation State**: Shows translated lyrics with language selector
6. **Similar Songs State**: Shows recommended similar tracks
7. **Song Meaning State**: Shows AI analysis of song meaning

## Manual Search

If automatic song identification fails, users can:

1. Enter song title and artist manually
2. Click "Search Lyrics" to perform a manual search
3. View lyrics from the manual search result

## Permissions

This extension requires the following permissions:
- `tabCapture`: To capture audio from tabs
- `activeTab`: To interact with the active tab
- `storage`: To store user preferences
- `offscreen`: To process audio in the background

## Development

For development without a running server, the extension includes mock responses. To test with the actual server:

1. Start the Lyrika server
2. Comment out the `return await mockServerResponse();` line in `background.js`
3. The extension will then make actual API calls to the server

## Troubleshooting

- If audio capture isn't working, ensure the tab you're trying to identify music from is actively playing audio
- If the server connection fails, verify the API_BASE_URL is correct and the server is running
- Chrome's permission model requires user interaction before capturing audio; always click the extension icon first

## Browser Compatibility

Currently optimized for:
- Google Chrome (version 88+)
- Microsoft Edge (version 88+) 