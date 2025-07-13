#!/usr/bin/env python3
"""
Lyrika Server
Flask application serving as backend for the Lyrika browser extension.
"""

import logging
import os

from api.acrcloud import identify_song_from_audio
from api.gemini import explain_song_meaning, get_lyrics_by_gemini, get_similar_songs
from api.gemini import is_configured as gemini_configured
from api.gemini import translate_lyrics
from api.genius import get_lyrics_by_song
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("lyrika_server")

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing


@app.route("/api/health", methods=["GET"])
def health_check():
    """Simple health check endpoint."""
    gemini_status = "available" if gemini_configured() else "unavailable"
    logger.info(f"Health check: Gemini API is {gemini_status}")

    return jsonify(
        {
            "status": "success",
            "message": "Lyrika API is running",
            "gemini_status": gemini_status,
        }
    )


@app.route("/api/identify", methods=["POST"])
def identify_song():
    """
    Identify a song from audio data sent by the extension.

    Expected request format:
    - audio_data: Base64 encoded audio data (required)
    """
    if not request.is_json:
        return jsonify({"status": "error", "message": "Request must be JSON"}), 400

    data = request.json
    audio_data = data.get("audio_data")

    if not audio_data:
        return jsonify({"status": "error", "message": "Missing audio data"}), 400

    try:
        # Identify the song using ACRCloud
        logger.info("Identifying song using ACRCloud")
        song_info = identify_song_from_audio(audio_data)

        if song_info["status"] == "success":
            # Get lyrics from Genius
            title = song_info.get("title")
            artist = song_info.get("artist")
            logger.info(
                f"Song identified: '{title}' by '{artist}', fetching lyrics from Genius"
            )
            lyrics_info = get_lyrics_by_song(title, artist)

            # Check if Genius returned lyrics
            lyrics = lyrics_info.get("lyrics", "")
            lyrics_source = lyrics_info.get("lyrics_source", "genius")
            formatting_source = lyrics_info.get("formatting", "basic")

            # If Genius didn't return lyrics, try Gemini as a fallback
            if not lyrics or lyrics.strip() == "":
                logger.info(
                    f"No lyrics found from Genius for '{title}' by '{artist}', trying Gemini API"
                )
                gemini_lyrics_info = get_lyrics_by_gemini(title, artist)

                if gemini_lyrics_info["status"] == "success":
                    lyrics = gemini_lyrics_info.get("lyrics", "")
                    lyrics_source = "gemini"
                    formatting_source = "gemini"
                    logger.info(
                        f"Successfully retrieved lyrics from Gemini API for '{title}' by '{artist}'"
                    )
                else:
                    logger.warning(
                        f"Gemini API also couldn't find lyrics for '{title}' by '{artist}'"
                    )

            # Combine results
            result = {
                "status": "success",
                "title": title,
                "artist": artist,
                "album": song_info.get("album", ""),
                "lyrics": lyrics,
                "youtubeId": song_info.get("youtubeId"),
                "spotifyId": song_info.get("spotifyId"),
                "albumArtwork": song_info.get("albumArtwork"),
                "lyrics_source": lyrics_source,
                "formatting": formatting_source,
            }
            return jsonify(result)
        else:
            logger.warning(
                f"Failed to identify song: {song_info.get('message', 'Unknown error')}"
            )
            return jsonify(song_info)

    except Exception as e:
        logger.exception(f"Error in song identification: {str(e)}")
        return (
            jsonify(
                {"status": "error", "message": f"Failed to process audio: {str(e)}"}
            ),
            500,
        )


@app.route("/api/lyrics", methods=["GET"])
def get_lyrics():
    """
    Get lyrics for a song by title and artist.

    Expected query parameters:
    - title: Song title (required)
    - artist: Artist name (optional)
    """
    title = request.args.get("title")
    artist = request.args.get("artist", "")
    print(f"Fetching lyrics for {title} by {artist}")
    if not title:
        return jsonify({"status": "error", "message": "Missing song title"}), 400

    try:
        logger.info(f"Fetching lyrics for '{title}' by '{artist}' from Genius")
        lyrics_info = get_lyrics_by_song(title, artist)

        # Check if Genius returned lyrics
        lyrics = lyrics_info.get("lyrics", "")
        lyrics_source = lyrics_info.get("lyrics_source", "genius")
        formatting_source = lyrics_info.get("formatting", "basic")

        # If Genius didn't return lyrics or returned an error, try Gemini as a fallback
        if not lyrics or lyrics.strip() == "" or lyrics_info.get("status") == "error":
            logger.info(
                f"No lyrics found from Genius for '{title}' by '{artist}', trying Gemini API"
            )
            gemini_lyrics_info = get_lyrics_by_gemini(title, artist)

            if gemini_lyrics_info["status"] == "success":
                # Replace the Genius response with Gemini's
                lyrics_info = gemini_lyrics_info
                lyrics_info["lyrics_source"] = "gemini"
                lyrics_info["formatting"] = "gemini"
                logger.info(
                    f"Successfully retrieved lyrics from Gemini API for '{title}' by '{artist}'"
                )
            else:
                logger.warning(
                    f"Gemini API also couldn't find lyrics for '{title}' by '{artist}'"
                )
                lyrics_info["lyrics_source"] = "none"
        else:
            lyrics_info["lyrics_source"] = lyrics_source
            lyrics_info["formatting"] = formatting_source

        return jsonify(lyrics_info)
    except Exception as e:
        logger.exception(f"Error fetching lyrics: {str(e)}")
        return (
            jsonify(
                {"status": "error", "message": f"Failed to fetch lyrics: {str(e)}"}
            ),
            500,
        )


@app.route("/api/translate_lyrics", methods=["POST"])
def translate():
    """
    Translate lyrics to a target language using Gemini API.

    Expected request format:
    - lyrics: The lyrics to translate (required)
    - source_lang: Source language (optional, defaults to "auto")
    - target_lang: Target language (required)
    """
    if not request.is_json:
        return jsonify({"status": "error", "message": "Request must be JSON"}), 400

    data = request.json
    lyrics = data.get("lyrics")
    source_lang = data.get("source_lang", "auto")
    target_lang = data.get("target_lang")

    if not lyrics:
        return jsonify({"status": "error", "message": "Missing lyrics"}), 400

    if not target_lang:
        return jsonify({"status": "error", "message": "Missing target language"}), 400

    try:
        logger.info(f"Translating lyrics from {source_lang} to {target_lang}")
        result = translate_lyrics(lyrics, source_lang, target_lang)
        logger.info(f"Translation completed using: {result.get('api_used', 'unknown')}")
        return jsonify(result)
    except Exception as e:
        logger.exception(f"Error translating lyrics: {str(e)}")
        return (
            jsonify(
                {"status": "error", "message": f"Failed to translate lyrics: {str(e)}"}
            ),
            500,
        )


@app.route("/api/explain_meaning", methods=["POST"])
def explain_meaning():
    """
    Get an explanation of the meaning of a song using Gemini API.

    Expected request format:
    - title: Song title (required)
    - artist: Artist name (required)
    - lyrics: Song lyrics (required)
    """
    if not request.is_json:
        return jsonify({"status": "error", "message": "Request must be JSON"}), 400

    data = request.json
    title = data.get("title")
    artist = data.get("artist")
    lyrics = data.get("lyrics")

    if not title or not artist or not lyrics:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Missing required fields (title, artist, or lyrics)",
                }
            ),
            400,
        )

    try:
        logger.info(f"Explaining meaning for '{title}' by '{artist}'")
        result = explain_song_meaning(title, artist, lyrics)
        logger.info(
            f"Meaning explanation completed using: {result.get('api_used', 'unknown')}"
        )

        # If Gemini returned an error and we have lyrics, we could try to provide a basic analysis
        if result.get("status") == "error" and "gemini_error" in result.get(
            "api_used", ""
        ):
            logger.info("Gemini API failed, providing basic analysis")
            # You could implement a simple analysis here if needed
            pass

        return jsonify(result)
    except Exception as e:
        logger.exception(f"Error explaining song meaning: {str(e)}")
        return (
            jsonify(
                {
                    "status": "error",
                    "message": f"Failed to explain song meaning: {str(e)}",
                }
            ),
            500,
        )


@app.route("/api/similar_songs", methods=["POST"])
def similar_songs():
    """
    Get recommendations for similar songs using Gemini API.

    Expected request format:
    - title: Song title (required)
    - artist: Artist name (required)
    - lyrics: Song lyrics (required)
    """
    if not request.is_json:
        return jsonify({"status": "error", "message": "Request must be JSON"}), 400

    data = request.json
    title = data.get("title")
    artist = data.get("artist")
    lyrics = data.get("lyrics")

    if not title or not artist or not lyrics:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Missing required fields (title, artist, or lyrics)",
                }
            ),
            400,
        )

    try:
        logger.info(f"Finding similar songs for '{title}' by '{artist}'")
        result = get_similar_songs(title, artist, lyrics)
        logger.info(
            f"Similar songs search completed using: {result.get('api_used', 'unknown')}"
        )
        return jsonify(result)
    except Exception as e:
        logger.exception(f"Error finding similar songs: {str(e)}")
        return (
            jsonify(
                {"status": "error", "message": f"Failed to get similar songs: {str(e)}"}
            ),
            500,
        )


@app.route("/api/debug/gemini_status", methods=["GET"])
def debug_gemini_status():
    """Debug endpoint to check Gemini API configuration status"""
    is_configured = gemini_configured()
    api_key_present = bool(os.environ.get("GEMINI_API_KEY", ""))

    logger.info(
        f"Debug request for Gemini status: configured={is_configured}, key_present={api_key_present}"
    )

    return jsonify(
        {
            "status": "success",
            "gemini_configured": is_configured,
            "api_key_present": api_key_present,
            "message": (
                "Gemini API is properly configured"
                if is_configured
                else "Gemini API is not configured"
            ),
        }
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV") == "development" or True

    # Log startup information
    logger.info(f"Starting Lyrika server on port {port}")
    logger.info(f"Debug mode: {debug}")
    logger.info(f"Gemini API configured: {gemini_configured()}")

    app.run(host="0.0.0.0", port=port, debug=debug)
