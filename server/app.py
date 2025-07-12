#!/usr/bin/env python3
"""
Lyrika Server
Flask application serving as backend for the Lyrika browser extension.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from api.acrcloud import identify_song_from_audio
from api.genius import get_lyrics_by_song

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

@app.route('/api/health', methods=['GET'])
def health_check():
    """Simple health check endpoint."""
    return jsonify({
        'status': 'success',
        'message': 'Lyrika API is running'
    })

@app.route('/api/identify', methods=['POST'])
def identify_song():
    """
    Identify a song from audio data sent by the extension.
    
    Expected request format:
    - audio_data: Base64 encoded audio data (required)
    """
    if not request.is_json:
        return jsonify({
            'status': 'error',
            'message': 'Request must be JSON'
        }), 400
    
    data = request.json
    audio_data = data.get('audio_data')
    
    if not audio_data:
        return jsonify({
            'status': 'error',
            'message': 'Missing audio data'
        }), 400
    
    try:
        # Identify the song using ACRCloud
        song_info = identify_song_from_audio(audio_data)
        
        if song_info['status'] == 'success':
            # Get lyrics from Genius
            title = song_info.get('title')
            artist = song_info.get('artist')
            lyrics_info = get_lyrics_by_song(title, artist)
            
            # Combine results
            result = {
                'status': 'success',
                'title': title,
                'artist': artist,
                'lyrics': lyrics_info.get('lyrics', ''),
                'youtubeId': song_info.get('youtubeId'),
                'spotifyId': song_info.get('spotifyId')
            }
            return jsonify(result)
        else:
            return jsonify(song_info)
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to process audio: {str(e)}'
        }), 500

@app.route('/api/lyrics', methods=['GET'])
def get_lyrics():
    """
    Get lyrics for a song by title and artist.
    
    Expected query parameters:
    - title: Song title (required)
    - artist: Artist name (optional)
    """
    title = request.args.get('title')
    artist = request.args.get('artist', '')
    
    if not title:
        return jsonify({
            'status': 'error',
            'message': 'Missing song title'
        }), 400
    
    try:
        lyrics_info = get_lyrics_by_song(title, artist)
        return jsonify(lyrics_info)
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to fetch lyrics: {str(e)}'
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug) 