"""
Genius API Integration

Handles fetching lyrics using the Genius API.
"""

import os
import requests
import re
import time
import random
from bs4 import BeautifulSoup

# Genius API configuration
GENIUS_ACCESS_TOKEN = os.environ.get('GENIUS_ACCESS_TOKEN', '')
GENIUS_BASE_URL = "https://api.genius.com"

def get_lyrics_by_song(title, artist=''):
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
            lyrics = scrape_lyrics(song_url)
            if lyrics:
                return {
                    'status': 'success',
                    'title': title,
                    'artist': artist,
                    'lyrics': lyrics,
                    'source_url': song_url
                }
        
        # If we get here, we couldn't find lyrics
        return {
            'status': 'error',
            'message': f"Could not find lyrics for {title} by {artist}",
            'title': title,
            'artist': artist,
            'lyrics': ''
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': f"Error fetching lyrics: {str(e)}",
            'title': title,
            'artist': artist,
            'lyrics': ''
        }

def search_song(search_term):
    """
    Search for a song on Genius.
    
    Args:
        search_term (str): Search term (title and artist)
    
    Returns:
        str: URL of the song page, or None if not found
    """
    headers = {'Authorization': f"Bearer {GENIUS_ACCESS_TOKEN}"}
    params = {'q': search_term}
    
    response = requests.get(
        f"{GENIUS_BASE_URL}/search", 
        headers=headers,
        params=params
    )
    
    if response.status_code == 200:
        data = response.json()
        hits = data.get('response', {}).get('hits', [])
        
        # Return URL of first hit if any
        if hits:
            return hits[0]['result']['url']
    
    return None

def scrape_lyrics(url):
    """
    Scrape lyrics from a Genius song page.
    
    Args:
        url (str): URL of the Genius song page
    
    Returns:
        str: Lyrics text, or empty string if not found
    """
    try:
        # Send request with user agent
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find lyrics container (may change based on Genius website structure)
            lyrics_div = soup.find('div', class_=re.compile(r"Lyrics__Container.*"))
            
            if not lyrics_div:
                # Try alternate class if first method fails
                lyrics_div = soup.find('div', class_="lyrics")
            
            if lyrics_div:
                # Extract and clean lyrics
                lyrics = lyrics_div.get_text()
                
                # Clean up lyrics text
                lyrics = re.sub(r'\[.*?\]', '', lyrics)  # Remove [Verse], [Chorus], etc.
                lyrics = re.sub(r'\n{3,}', '\n\n', lyrics)  # Remove excessive newlines
                lyrics = lyrics.strip()
                
                return lyrics
            
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
            'status': 'success',
            'title': 'Bohemian Rhapsody',
            'artist': 'Queen',
            'lyrics': """Is this the real life? Is this just fantasy?
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
            'source_url': 'https://genius.com/Queen-bohemian-rhapsody-lyrics'
        }
    else:
        # Generate some generic mock lyrics based on the title and artist
        mock_lyrics = f"This is a mock lyric for {title}"
        if artist:
            mock_lyrics += f" by {artist}.\n\nThis is generated for testing purposes.\n"
            mock_lyrics += "The actual lyrics would be fetched from Genius in production."
        
        return {
            'status': 'success',
            'title': title,
            'artist': artist,
            'lyrics': mock_lyrics,
            'source_url': 'https://example.com/mock-lyrics'
        } 