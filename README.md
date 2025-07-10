# Lyrika

A browser extension that listens to audio playing in any browser tab, identifies the song, and displays its lyrics, turning your browser into a smart, lyrics-aware music player.

## Problem Statement

Lyrika eliminates the manual, multi-step process of searching for lyrics for a song you're currently listening to online. This is perfect for API orchestration and provides a tangible, useful tool for personal use.

## Key Features

- **One-Click Recognition**: Click the extension icon to start listening to the active tab's audio
- **Real-time Identification**: View "Listening..." status, then see Song Title and Artist upon successful match
- **Lyrics Display**: Full lyrics for the identified song appear in the popup
- **Copy to Clipboard**: Click the song title to copy "Song Title by Artist" to clipboard
- **Direct Song Link**: Access a clickable YouTube icon linking to the song's video
- **Graceful Error Handling**: Clear feedback for common edge-case scenarios

## Tech Stack

- **Extension Framework**: Plain JavaScript, HTML, CSS with Manifest V3
- **Primary API**: ACRCloud API (14-day free trial for development and demos)
- **Secondary API**: Shazam API on RapidAPI (for long-term use with 500 calls/month free tier)
- **Lyrics API**: Genius API for retrieving full, non-synced lyrics
- **Core Browser APIs**: chrome.tabCapture for audio and navigator.clipboard for the copy feature

## Folder Structure

```
lyrika/
├── manifest.json
├── assets/
│   └── icons/
│       ├── icon16.png
│       ├── icon48.png
│       └── icon128.png
├── css/
│   └── popup.css
├── js/
│   ├── api/
│   │   ├── acrcloud-client.js  <-- Build this for the hackathon (14 days free unlimited)
│   │   └── shazam-client.js    <-- Placeholder for after (around 17 songs possible searches per day, not suitable for hackathon)
│   ├── background.js
│   └── popup.js
└── popup.html
```

## Implementation Plan for Edge Cases

### Instrumental Songs
- **Trigger**: ACRCloud identifies the song, but Genius API returns no lyrics
- **Solution**: Display message: "Song Identified! This is an instrumental track."

### Cover Versions
- **Trigger**: ACRCloud identifies cover artist, but Genius has no lyrics for that version
- **Solution**: Implement fallback search with just song title and display a note: "Displaying original version lyrics."

### Background Noise/Dialogue
- **Trigger**: ACRCloud fails to get a match
- **Solution**: Display message: "Couldn't hear a clear song. Please ensure music is playing without too much background noise."

### Saving Song References
- **Solution 1 (Link)**: Create clickable YouTube icon using external_metadata.youtube.vid
- **Solution 2 (Copy)**: Add click listener to song title to copy "Song Title by Artist" to clipboard

## Hackathon Strategy Overview

- **MVP First**: Focus on core functionality before extras
- **API Key Security**: Use environment variables and proper security practices
- **Testing Framework**: Create test pages with sample audio
- **Fallback Mechanisms**: Implement manual input when recognition fails
- **Performance Optimization**: Add debounce and processing state tracking
- **Demo Preparation**: Create reliable test songs and documentation

See `ROLES.md` for detailed implementation tasks for each team member.

## API Key Security

For security of API keys, the project uses:

1. Environment variables with build process
2. Secure backend proxy approach (optional)
3. First-time setup flow (optional)

See `ROLES.md` for detailed security implementation.