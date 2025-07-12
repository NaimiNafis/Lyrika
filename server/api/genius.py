"""
Genius API Integration

Handles fetching lyrics using the Genius API.
"""

import os
import random
import re
import time

import requests
from bs4 import BeautifulSoup

# Genius API configuration
GENIUS_ACCESS_TOKEN = os.environ.get("GENIUS_ACCESS_TOKEN", "")
GENIUS_BASE_URL = "https://api.genius.com"


def get_lyrics_by_song(title, artist=""):
    """
    Get lyrics for a song using the Genius API.

    Args:
        title (str): Song title
        artist (str, optional): Artist name

    Returns:
        dict: Lyrics information
    """
    try:
        # For development/testing, use mock response if no API token
        if not GENIUS_ACCESS_TOKEN:
            print("Warning: Using mock lyrics as Genius API token is not set")
            return mock_get_lyrics(title, artist)

        # Search for the song
        search_term = f"{title} {artist}".strip()
        song_url = search_song(search_term)

        if not song_url:
            # Try again with just the title if artist was provided
            if artist:
                song_url = search_song(title)

        # Fetch and extract lyrics
        if song_url:
            raw_lyrics = scrape_lyrics(song_url)
            if raw_lyrics:
                # Try to clean up the lyrics using Gemini if available
                try:
                    from api.gemini import format_lyrics_with_gemini, is_configured
                    
                    if is_configured():
                        print(f"Using Gemini to format lyrics for {title} by {artist}")
                        formatted_result = format_lyrics_with_gemini(raw_lyrics, title, artist)
                        
                        # If Gemini formatting was successful, use those lyrics
                        if formatted_result and formatted_result.get("status") == "success":
                            lyrics = formatted_result.get("lyrics", raw_lyrics)
                            return {
                                "status": "success",
                                "title": title,
                                "artist": artist,
                                "lyrics": lyrics,
                                "source_url": song_url,
                                "formatting": "gemini"
                            }
                except Exception as formatting_error:
                    print(f"Error using Gemini for formatting: {formatting_error}")
                    # Continue with original lyrics if Gemini formatting fails

                # Return original lyrics if Gemini formatting wasn't available or failed
                return {
                    "status": "success",
                    "title": title,
                    "artist": artist,
                    "lyrics": raw_lyrics,
                    "source_url": song_url,
                    "formatting": "basic"
                }

        # If we get here, we couldn't find lyrics
        return {
            "status": "error",
            "message": f"Could not find lyrics for {title} by {artist}",
            "title": title,
            "artist": artist,
            "lyrics": "",
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error fetching lyrics: {str(e)}",
            "title": title,
            "artist": artist,
            "lyrics": "",
        }


def search_song(search_term):
    """
    Search for a song on Genius.

    Args:
        search_term (str): Search term (title and artist)

    Returns:
        str: URL of the song page, or None if not found
    """
    headers = {"Authorization": f"Bearer {GENIUS_ACCESS_TOKEN}"}
    params = {"q": search_term}

    response = requests.get(f"{GENIUS_BASE_URL}/search", headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        hits = data.get("response", {}).get("hits", [])

        # Return URL of first hit if any
        if hits:
            return hits[0]["result"]["url"]

    return None


def scrape_lyrics(url):
    """
    Scrape lyrics from a Genius song page.

    Args:
        url (str): URL of the Genius song page

    Returns:
        str: Clean lyrics text, or empty string if not found
    """
    try:
        # Send request with user agent
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
        }
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            # Find lyrics container (may change based on Genius website structure)
            lyrics_div = soup.find("div", class_=re.compile(r"Lyrics__Container.*"))

            if not lyrics_div:
                # Try alternate class if first method fails
                lyrics_div = soup.find("div", class_="lyrics")

            if lyrics_div:
                # Extract lyrics and perform cleaning
                
                # Remove unwanted elements
                for unwanted in lyrics_div.select('.InlineAnnotation__Container, .ReferentFragmentVariantdesktop__Container'):
                    unwanted.decompose()
                
                # Extract raw lyrics text
                lyrics = lyrics_div.get_text()

                # Clean up lyrics text
                lyrics = re.sub(r'\d+ Contributors.*?Read More', '', lyrics, flags=re.DOTALL)  # Remove contributors, translations etc.
                lyrics = re.sub(r'Translations.*?Lyrics', '', lyrics, flags=re.DOTALL)  # Remove translations section
                lyrics = re.sub(r'[\w\s]+ Lyrics', '', lyrics)  # Remove "Song Title Lyrics" text
                lyrics = re.sub(r'\[.*?\]', '', lyrics)  # Remove [Verse], [Chorus], etc.
                
                # More aggressive cleaning of undesirable elements
                lyrics = re.sub(r'Embed$', '', lyrics, flags=re.MULTILINE)  # Remove "Embed" text
                lyrics = re.sub(r'Share URL$', '', lyrics, flags=re.MULTILINE)  # Remove "Share URL" text
                lyrics = re.sub(r'Copy$', '', lyrics, flags=re.MULTILINE)  # Remove "Copy" text
                
                # Fix line breaks issues
                
                # Step 1: Normalize all line breaks
                lyrics = re.sub(r'\r\n', '\n', lyrics)
                
                # Step 2: Join words broken across lines (lowercase to lowercase)
                lyrics = re.sub(r'([a-z])[\s]*\n[\s]*([a-z])', r'\1 \2', lyrics)
                
                # Step 3: Ensure proper spacing around punctuation
                lyrics = re.sub(r'([.,;:!?])[\s]*\n', r'\1\n', lyrics)
                
                # Step 4: Preserve intentional line breaks after punctuation
                lyrics = re.sub(r'([.,;:!?])[\s]*([A-Z])', r'\1\n\2', lyrics)
                
                # Step 5: Remove excess blank lines but preserve verse structure
                lyrics = re.sub(r'\n{3,}', '\n\n', lyrics)
                
                # Remove leading/trailing whitespace from each line
                lyrics_lines = [line.strip() for line in lyrics.split('\n')]
                lyrics = '\n'.join(lyrics_lines)
                
                # Final cleanup of excessive whitespace and blank lines
                lyrics = re.sub(r' {2,}', ' ', lyrics)  # Replace multiple spaces with single space
                lyrics = re.sub(r'^\n+', '', lyrics)  # Remove leading blank lines
                lyrics = re.sub(r'\n+$', '', lyrics)  # Remove trailing blank lines
                
                return lyrics.strip()

    except Exception as e:
        print(f"Error scraping lyrics: {e}")

    return ""


def mock_get_lyrics(title, artist):
    """
    Mock lyrics function for development and testing.

    Args:
        title (str): Song title
        artist (str): Artist name

    Returns:
        dict: Mock lyrics result
    """
    if "bohemian" in title.lower() or "rhapsody" in title.lower():
        return {
            "status": "success",
            "title": "Bohemian Rhapsody",
            "artist": "Queen",
            "lyrics": """Is this the real life? Is this just fantasy?
Caught in a landslide, no escape from reality
Open your eyes, look up to the skies and see
I'm just a poor boy, I need no sympathy
Because I'm easy come, easy go, little high, little low
Any way the wind blows doesn't really matter to me, to me

Mama, just killed a man
Put a gun against his head, pulled my trigger, now he's dead
Mama, life had just begun
But now I've gone and thrown it all away
Mama, ooh, didn't mean to make you cry
If I'm not back again this time tomorrow
Carry on, carry on as if nothing really matters""",
            "source_url": "https://genius.com/Queen-bohemian-rhapsody-lyrics",
        }
    else:
        # Generate some generic mock lyrics based on the title and artist
        mock_lyrics = f"This is a mock lyric for {title}"
        if artist:
            mock_lyrics += f" by {artist}.\n\nThis is generated for testing purposes.\n"
            mock_lyrics += (
                "The actual lyrics would be fetched from Genius in production."
            )

        return {
            "status": "success",
            "title": title,
            "artist": artist,
            "lyrics": mock_lyrics,
            "source_url": "https://example.com/mock-lyrics",
        }
