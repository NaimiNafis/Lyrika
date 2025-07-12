"""
ACRCloud API Integration

Handles song identification using the ACRCloud API.
"""

import base64
import hashlib
import hmac
import io
import json
import os
import subprocess
import tempfile
import time
from urllib.parse import urlencode

import requests

# ACRCloud API configuration
ACR_HOST = os.environ.get("ACRCLOUD_HOST", "identify-ap-southeast-1.acrcloud.com")
ACR_ACCESS_KEY = os.environ.get("ACRCLOUD_ACCESS_KEY", "")
ACR_ACCESS_SECRET = os.environ.get("ACRCLOUD_ACCESS_SECRET", "")
ACR_TIMEOUT = int(os.environ.get("ACRCLOUD_TIMEOUT", 10))


def identify_song_from_audio(audio_data):
    """
    Identify a song using ACRCloud API.

    Args:
        audio_data (str): Base64-encoded audio data

    Returns:
        dict: Song identification result
    """
    try:
        # Convert base64 string to binary
        binary_data = base64.b64decode(audio_data)

        # Prepare request
        http_method = "POST"
        http_uri = "/v1/identify"
        data_type = "audio"
        signature_version = "1"
        timestamp = str(int(time.time()))

        # Generate signature
        string_to_sign = "\n".join(
            [
                http_method,
                http_uri,
                ACR_ACCESS_KEY,
                data_type,
                signature_version,
                timestamp,
            ]
        )

        sign = base64.b64encode(
            hmac.new(
                ACR_ACCESS_SECRET.encode("utf-8"),
                string_to_sign.encode("utf-8"),
                digestmod=hashlib.sha1,
            ).digest()
        ).decode("utf-8")

        # Prepare request data
        files = {"sample": binary_data}

        data = {
            "access_key": ACR_ACCESS_KEY,
            "data_type": data_type,
            "signature": sign,
            "signature_version": signature_version,
            "timestamp": timestamp,
        }

        # Make request to ACRCloud
        url = f"https://{ACR_HOST}{http_uri}"
        print(f"Making request to ACRCloud: {url}")
        print(
            f"ACR_ACCESS_KEY: {ACR_ACCESS_KEY[:10]}..."
        )  # Show first 10 chars for debugging
        print(f"Audio data size: {len(binary_data)} bytes")
        print(f"Request data: {data}")
        print(f"String to sign: {string_to_sign}")
        print(f"Generated signature: {sign}")

        response = requests.post(url, files=files, data=data, timeout=ACR_TIMEOUT)

        if response.status_code == 200:
            result = response.json()

            # For development/testing, use this mock response instead
            if not ACR_ACCESS_KEY:
                print(
                    "Warning: Using mock response as ACRCloud credentials are not set"
                )
                return mock_identify_song()

            # Check if a match was found
            if (
                result.get("status", {}).get("code") == 0
                and "metadata" in result
                and "music" in result["metadata"]
                and len(result["metadata"]["music"]) > 0
            ):

                # Extract song information
                music = result["metadata"]["music"][0]
                title = music.get("title", "")
                artists = music.get("artists", [{}])
                artist = artists[0].get("name", "") if artists else ""

                # Extract YouTube ID if available
                youtube_id = None
                if 'external_metadata' in music and 'youtube' in music['external_metadata']:
                    youtube_id = music['external_metadata']['youtube'].get('vid')
                
                # Extract Spotify ID if available
                spotify_id = None
                if 'external_metadata' in music and 'spotify' in music['external_metadata'] and 'track' in music['external_metadata']['spotify']:
                    spotify_id = music['external_metadata']['spotify']['track'].get('id')

                return {
                    'status': 'success',
                    'title': title,
                    'artist': artist,
                    'youtubeId': youtube_id,
                    'spotifyId': spotify_id,
                    'raw': music  # Include raw data for debugging/future use
                }
            else:
                # No match found
                return {
                    "status": "error",
                    "message": "Could not identify song. Please ensure music is playing clearly.",
                }
        else:
            # API request failed
            return {
                "status": "error",
                "message": f"API request failed with status code {response.status_code}",
            }

    except Exception as e:
        return {"status": "error", "message": f"Error identifying song: {str(e)}"}


def mock_identify_song():
    """
    Mock song identification for development and testing.

    Returns:
        dict: Mock song identification result
    """
    # 80% chance of success
    if time.time() % 10 > 2:  # Simple way to randomize
        return {
            "status": "success",
            "title": "Bohemian Rhapsody",
            "artist": "Queen",
            "youtubeId": "fJ9rUzIMcZQ",
            "raw": {
                "title": "Bohemian Rhapsody",
                "artists": [{"name": "Queen"}],
                "album": {"name": "A Night at the Opera"},
                "external_metadata": {"youtube": {"vid": "fJ9rUzIMcZQ"}},
            },
        }
    else:
        # Simulate error
        return {
            "status": "error",
            "message": "Could not identify song. Please ensure music is playing clearly.",
        }
