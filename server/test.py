"""
Simple ACRCloud song identification with clean output
"""

import base64
import hashlib
import hmac
import json
import os
import sys
import time

import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load credentials
access_key = os.getenv("ACRCLOUD_ACCESS_KEY")
access_secret = os.getenv("ACRCLOUD_ACCESS_SECRET")
host = os.getenv("ACRCLOUD_HOST", "identify-ap-southeast-1.acrcloud.com")

if not access_key or not access_secret:
    print("❌ Error: Missing ACRCloud credentials in .env file")
    sys.exit(1)


def identify_song(audio_file_path):
    """Identify a song and return clean results"""

    # Setup request parameters
    requrl = f"https://{host}/v1/identify"
    http_method = "POST"
    http_uri = "/v1/identify"
    data_type = "audio"
    signature_version = "1"
    timestamp = time.time()

    # Generate signature
    string_to_sign = (
        http_method
        + "\n"
        + http_uri
        + "\n"
        + access_key
        + "\n"
        + data_type
        + "\n"
        + signature_version
        + "\n"
        + str(timestamp)
    )

    signature = base64.b64encode(
        hmac.new(
            access_secret.encode("ascii"),
            string_to_sign.encode("ascii"),
            digestmod=hashlib.sha1,
        ).digest()
    ).decode("ascii")

    # Prepare request
    sample_bytes = os.path.getsize(audio_file_path)
    files = [("sample", ("audio.mp3", open(audio_file_path, "rb"), "audio/mpeg"))]
    data = {
        "access_key": access_key,
        "sample_bytes": sample_bytes,
        "timestamp": str(timestamp),
        "signature": signature,
        "data_type": data_type,
        "signature_version": signature_version,
    }

    # Make request
    response = requests.post(requrl, files=files, data=data)
    response.encoding = "utf-8"

    return response.json()


def extract_song_info(acrcloud_response):
    """Extract clean song information from ACRCloud response"""

    try:
        status = acrcloud_response.get("status", {})

        if status.get("code") != 0:
            return {"status": "error", "message": status.get("msg", "Unknown error")}

        # Get the first music match
        music_data = acrcloud_response["metadata"]["music"][0]

        # Extract basic info
        title = music_data["title"]
        artist = music_data["artists"][0]["name"]
        album = music_data.get("album", {}).get("name", "")

        # Extract YouTube ID if available
        youtube_id = None
        external_metadata = music_data.get("external_metadata", {})
        if "youtube" in external_metadata:
            youtube_id = external_metadata["youtube"].get("vid")

        return {
            "status": "success",
            "title": title,
            "artist": artist,
            "album": album,
            "youtubeId": youtube_id,
            "duration_ms": music_data.get("duration_ms"),
            "score": music_data.get("score"),
            "raw": acrcloud_response,
        }

    except (KeyError, IndexError) as e:
        return {"status": "error", "message": f"Failed to parse response: {e}"}


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python clean_test.py <audio_file>")
        sys.exit(1)

    audio_file = sys.argv[1]

    # Identify the song
    raw_response = identify_song(audio_file)
    song_info = extract_song_info(raw_response)

    # Print results
    if song_info["status"] == "success":
        # print("\n✅ Song Identified!")
        print(f"🎵 Title: {song_info['title']}")
        print(f"🎤 Artist: {song_info['artist']}")
        # if song_info["album"]:
        #     print(f"💿 Album: {song_info['album']}")
        # if song_info["youtubeId"]:
        #     print(
        #         f"📺 YouTube: https://www.youtube.com/watch?v={song_info['youtubeId']}"
        #     )
        # print(f"🎯 Confidence: {song_info['score']}%")

        # Just the name format you requested
        # print(f"\n📋 Song: {song_info['title']} by {song_info['artist']}")

    else:
        print(f"\n❌ Error: {song_info['message']}")
