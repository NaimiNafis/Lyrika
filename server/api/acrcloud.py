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
GENIUS_ACCESS_TOKEN = os.environ.get("GENIUS_ACCESS_TOKEN", "")
GENIUS_BASE_URL = "https://api.genius.com"
HEADERS = {"Authorization": f"Bearer {GENIUS_ACCESS_TOKEN}"}


def search_song(song_name: str):
    url = f"{GENIUS_BASE_URL}/search?q={song_name}"
    response = requests.get(url, headers=HEADERS)
    data = response.json()

    if response.status_code != 200:
        print(f"Error: {response.status_code} - {data.get('error_description')}")
        return None

    if not data["response"]["hits"]:
        print("No song found.")
        return None

    song = data["response"]["hits"][0]["result"]
    return {
        "title": song["title"],
        "artist": song["primary_artist"]["name"],
        "song_url": song["url"],
        "artist_url": song["primary_artist"]["url"],
        "thumbnail": song["song_art_image_thumbnail_url"],
    }


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

        # Check audio format and size
        # print(f"Audio data length: {len(audio_data)} characters")
        # print(f"Binary data size: {len(binary_data)} bytes")

        # Convert WebM to WAV for ACRCloud compatibility using ffmpeg
        try:
            # Create temporary files for conversion
            with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as webm_file:
                webm_file.write(binary_data)
                webm_path = webm_file.name

            wav_path = webm_path.replace(".webm", ".wav")

            # Use ffmpeg to convert WebM to WAV with better quality for ACRCloud
            cmd = [
                "ffmpeg",
                "-i",
                webm_path,
                "-acodec",
                "pcm_s16le",  # 16-bit PCM
                "-ar",
                "44100",  # 44.1kHz sample rate (CD quality)
                "-ac",
                "2",  # Stereo (ACRCloud prefers stereo)
                "-af",
                "volume=2.0",  # Increase volume
                "-y",  # Overwrite output file
                wav_path,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                # Read the converted WAV file
                with open(wav_path, "rb") as wav_file:
                    wav_data = wav_file.read()

                # print(f"Converted to WAV: {len(wav_data)} bytes")
                binary_data = wav_data  # Use the converted WAV data
            else:
                print(f"FFmpeg conversion failed: {result.stderr}")

            # Clean up temporary files
            os.unlink(webm_path)
            if os.path.exists(wav_path):
                os.unlink(wav_path)

        except Exception as e:
            print(f"Error converting audio: {e}")
            # Fallback to original data if conversion fails
            pass

        # Save the converted WAV file for manual inspection
        try:
            with open("server/debug_output.wav", "wb") as debug_file:
                debug_file.write(binary_data)
        except Exception as e:
            print(f"Error saving debug_output.wav: {e}")

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
        # ACRCloud expects the audio file to be sent as 'sample' in multipart form data
        files = {"sample": ("sample.wav", binary_data, "audio/wav")}

        data = {
            "access_key": ACR_ACCESS_KEY,
            "data_type": data_type,
            "signature": sign,
            "signature_version": signature_version,
            "timestamp": timestamp,
            "sample_bytes": str(
                len(binary_data)
            ),  # Add sample_bytes as required by ACRCloud
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

        response = requests.post(url, files=files, data=data)
        # print(f"ACRCloud response status code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            # print(f"ACRCloud response: {json.dumps(result, indent=2)}")

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
                album_name = music.get("album", {}).get("name", "")

                # Extract YouTube ID if available
                youtube_id = None
                if (
                    "external_metadata" in music
                    and "youtube" in music["external_metadata"]
                ):
                    youtube_id = music["external_metadata"]["youtube"].get("vid")

                # Extract Spotify ID if available
                spotify_id = None
                if (
                    "external_metadata" in music
                    and "spotify" in music["external_metadata"]
                ):
                    spotify_id = (
                        music["external_metadata"]["spotify"].get("track", {}).get("id")
                    )

                # Extract album artwork URLs
                singleArtwork = search_song(f"{title} {artist}")
                album_artwork = singleArtwork.get("thumbnail")

                return {
                    "status": "success",
                    "title": title,
                    "artist": artist,
                    "album": album_name,
                    "youtubeId": youtube_id,
                    "spotifyId": spotify_id,
                    "albumArtwork": album_artwork,
                    "raw": music,  # Include raw data for debugging/future use
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
            "album": "A Night at the Opera",
            "youtubeId": "fJ9rUzIMcZQ",
            "spotifyId": "6l8GvAyoUZwWDgF1e4822w",
            "albumArtwork": "https://i.scdn.co/image/ab67616d0000b273c8b444df094279e70d0ed856",
            "raw": {
                "title": "Bohemian Rhapsody",
                "artists": [{"name": "Queen"}],
                "album": {"name": "A Night at the Opera"},
                "external_metadata": {
                    "youtube": {"vid": "fJ9rUzIMcZQ"},
                    "spotify": {"track": {"id": "6l8GvAyoUZwWDgF1e4822w"}},
                },
            },
        }
    else:
        # Simulate error
        return {
            "status": "error",
            "message": "Could not identify song. Please ensure music is playing clearly.",
        }
