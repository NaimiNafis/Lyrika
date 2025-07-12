"""
Gemini API Integration

Handles AI-powered features using Google's Gemini API:
1. Lyrics translation
2. Song meaning explanations
3. Similar song recommendations
4. Lyrics generation (fallback when Genius doesn't have lyrics)
"""

import os
import logging
import google.generativeai as genai
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('gemini_api')

# Gemini API configuration
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
MODEL_NAME = "gemini-1.5-pro"  # Using the most capable model

# Configure the Gemini API
if GEMINI_API_KEY:
    logger.info("Gemini API key found, configuring API client")
    genai.configure(api_key=GEMINI_API_KEY)
else:
    logger.warning("No Gemini API key found in environment variables - will use mock data")

def is_configured() -> bool:
    """Check if Gemini API is configured properly"""
    configured = bool(GEMINI_API_KEY)
    logger.info(f"Gemini API configured: {configured}")
    return configured

def get_lyrics_by_gemini(title: str, artist: str) -> Dict[str, Any]:
    """
    Get lyrics for a song using Gemini when Genius API doesn't have them.
    
    Args:
        title (str): Song title
        artist (str): Artist name
    
    Returns:
        dict: Lyrics result
    """
    try:
        if not is_configured():
            logger.warning(f"Using mock lyrics for '{title}' by '{artist}'")
            return mock_lyrics(title, artist)
        
        logger.info(f"Calling Gemini API to get lyrics for '{title}' by '{artist}'")
        
        # Create the prompt for lyrics generation
        prompt = f"""
        Please provide the complete and accurate lyrics for the song "{title}" by "{artist}".
        
        Rules:
        1. Return ONLY the lyrics with proper formatting and line breaks
        2. Include all verses, chorus, and bridge sections in the correct order
        3. Do not include any explanations, notes, or comments
        4. If you don't know the exact lyrics, please state "I don't have the complete lyrics for this song" instead of making them up
        5. Preserve any stylistic elements like capitalization or punctuation as they appear in the original lyrics
        """
        
        # Generate the lyrics using Gemini
        model = genai.GenerativeModel(MODEL_NAME)
        logger.info(f"Sending lyrics request to Gemini model: {MODEL_NAME}")
        response = model.generate_content(prompt)
        
        if response and response.text:
            lyrics_text = response.text.strip()
            
            # Check if Gemini doesn't know the lyrics
            if "don't have" in lyrics_text.lower() and "lyrics" in lyrics_text.lower():
                logger.warning(f"Gemini doesn't have lyrics for '{title}' by '{artist}'")
                return {
                    "status": "error",
                    "message": "Lyrics not found",
                    "title": title,
                    "artist": artist,
                    "api_used": "gemini_no_lyrics"
                }
            
            logger.info("Successfully received lyrics from Gemini API")
            return {
                "status": "success",
                "title": title,
                "artist": artist,
                "lyrics": lyrics_text,
                "api_used": "gemini"
            }
        else:
            logger.error("Gemini API returned empty response for lyrics")
            return {
                "status": "error",
                "message": "Failed to generate lyrics",
                "title": title,
                "artist": artist,
                "api_used": "gemini_failed"
            }
    
    except Exception as e:
        logger.exception(f"Error in Gemini lyrics generation: {str(e)}")
        return {
            "status": "error", 
            "message": f"Error getting lyrics: {str(e)}",
            "title": title,
            "artist": artist,
            "api_used": "gemini_error"
        }

def translate_lyrics(lyrics: str, source_lang: str = "auto", target_lang: str = "French") -> Dict[str, Any]:
    """
    Translate song lyrics to the target language using Gemini.
    
    Args:
        lyrics (str): The original lyrics to translate
        source_lang (str): Source language (or "auto" for auto-detection)
        target_lang (str): Target language for translation
    
    Returns:
        dict: Translation result
    """
    try:
        if not is_configured():
            logger.warning(f"Using mock translation for {source_lang} -> {target_lang}")
            return mock_translate_lyrics(lyrics, target_lang)
        
        logger.info(f"Calling Gemini API for translation: {source_lang} -> {target_lang}")
        
        # Create the prompt for translation
        prompt = f"""
        Translate these lyrics from {source_lang} to {target_lang}:
        
        {lyrics}
        
        Rules:
        1. Keep the original structure, line breaks, and formatting intact
        2. Maintain the musicality and flow where possible
        3. Focus on conveying the meaning rather than literal translation
        4. Do not add explanations or notes - just provide the translated lyrics
        """
        
        # Generate the translation using Gemini
        model = genai.GenerativeModel(MODEL_NAME)
        logger.info(f"Sending translation request to Gemini model: {MODEL_NAME}")
        response = model.generate_content(prompt)
        
        if response and response.text:
            logger.info("Successfully received translation from Gemini API")
            return {
                "status": "success",
                "original_lyrics": lyrics,
                "translated_lyrics": response.text.strip(),
                "source_language": source_lang,
                "target_language": target_lang,
                "api_used": "gemini"
            }
        else:
            logger.error("Gemini API returned empty response for translation")
            return {
                "status": "error",
                "message": "Failed to generate translation",
                "original_lyrics": lyrics,
                "api_used": "gemini_failed"
            }
    
    except Exception as e:
        logger.exception(f"Error in Gemini translation: {str(e)}")
        return {
            "status": "error",
            "message": f"Error translating lyrics: {str(e)}",
            "original_lyrics": lyrics,
            "api_used": "gemini_error"
        }

def explain_song_meaning(title: str, artist: str, lyrics: str) -> Dict[str, Any]:
    """
    Analyze and explain the meaning behind a song using Gemini.
    
    Args:
        title (str): Song title
        artist (str): Artist name
        lyrics (str): Song lyrics
    
    Returns:
        dict: Song meaning analysis
    """
    try:
        if not is_configured():
            logger.warning(f"Using mock song meaning explanation for '{title}' by '{artist}'")
            return mock_explain_song_meaning(title, artist)
        
        logger.info(f"Calling Gemini API for song meaning: '{title}' by '{artist}'")
        
        # Create the prompt for song meaning analysis
        prompt = f"""
        Analyze these lyrics for "{title}" by "{artist}":
        
        {lyrics}
        
        Provide:
        1. Main theme and message of the song
        2. Cultural or historical context if relevant
        3. Hidden meanings or metaphors
        4. Personal interpretation of emotional impact
        
        Format your response with clear sections and keep the explanation concise but insightful (200-300 words total).
        """
        
        # Generate the analysis using Gemini
        model = genai.GenerativeModel(MODEL_NAME)
        logger.info(f"Sending song meaning request to Gemini model: {MODEL_NAME}")
        response = model.generate_content(prompt)
        
        if response and response.text:
            logger.info("Successfully received song meaning analysis from Gemini API")
            return {
                "status": "success",
                "title": title,
                "artist": artist,
                "meaning": response.text.strip(),
                "api_used": "gemini"
            }
        else:
            logger.error("Gemini API returned empty response for song meaning")
            return {
                "status": "error",
                "message": "Failed to analyze song meaning",
                "title": title,
                "artist": artist,
                "api_used": "gemini_failed"
            }
    
    except Exception as e:
        logger.exception(f"Error in Gemini song meaning analysis: {str(e)}")
        return {
            "status": "error", 
            "message": f"Error analyzing song meaning: {str(e)}",
            "title": title,
            "artist": artist,
            "api_used": "gemini_error"
        }

def get_similar_songs(title: str, artist: str, lyrics: str) -> Dict[str, Any]:
    """
    Get recommendations for similar songs based on the current song.
    
    Args:
        title (str): Song title
        artist (str): Artist name
        lyrics (str): Song lyrics
    
    Returns:
        dict: List of similar song recommendations
    """
    try:
        if not is_configured():
            logger.warning(f"Using mock similar songs for '{title}' by '{artist}'")
            return mock_similar_songs(title, artist)
        
        logger.info(f"Calling Gemini API for similar songs: '{title}' by '{artist}'")
        
        # Extract first few lines of lyrics for context (to keep prompt size reasonable)
        lyrics_preview = "\n".join(lyrics.split("\n")[:10])
        
        # Create the prompt for similar songs
        prompt = f"""
        Based on the song "{title}" by "{artist}" with these lyrics:
        
        {lyrics_preview}
        
        Recommend 5 similar songs with these criteria:
        1. Similar musical style or era
        2. Thematically related content
        3. Similar emotional tone
        4. From a mix of well-known and lesser-known artists
        
        Format your response as a JSON list with this structure:
        [
          {{
            "title": "Song Title",
            "artist": "Artist Name",
            "reason": "Brief explanation of why it's similar (1 sentence)",
            "year": "Release year (approximate is fine)"
          }},
          ...
        ]
        
        Return ONLY the JSON with no additional text or explanation.
        """
        
        # Generate the recommendations using Gemini
        model = genai.GenerativeModel(MODEL_NAME)
        logger.info(f"Sending similar songs request to Gemini model: {MODEL_NAME}")
        response = model.generate_content(prompt)
        
        if response and response.text:
            # Parse the JSON response
            import json
            try:
                logger.info("Successfully received similar songs from Gemini API")
                # Extract JSON from response (might be wrapped in markdown code block)
                text = response.text.strip()
                if "```json" in text:
                    text = text.split("```json")[1].split("```")[0].strip()
                elif "```" in text:
                    text = text.split("```")[1].strip()
                
                recommendations = json.loads(text)
                
                return {
                    "status": "success",
                    "title": title,
                    "artist": artist,
                    "recommendations": recommendations,
                    "api_used": "gemini"
                }
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                logger.error("Failed to parse JSON from Gemini API response")
                return {
                    "status": "error",
                    "message": "Failed to parse recommendations data",
                    "raw_response": response.text,
                    "api_used": "gemini_parse_error"
                }
        else:
            logger.error("Gemini API returned empty response for similar songs")
            return {
                "status": "error",
                "message": "Failed to generate recommendations",
                "title": title,
                "artist": artist,
                "api_used": "gemini_failed"
            }
    
    except Exception as e:
        logger.exception(f"Error in Gemini similar songs: {str(e)}")
        return {
            "status": "error",
            "message": f"Error getting similar songs: {str(e)}",
            "title": title,
            "artist": artist,
            "api_used": "gemini_error"
        }

# Mock responses for development when API key is not available

def mock_lyrics(title: str, artist: str) -> Dict[str, Any]:
    """Mock lyrics generation function for development and testing."""
    logger.info(f"Using mock lyrics for '{title}' by '{artist}'")
    
    mock_lyrics_text = f"""
    [Verse 1]
    This is a placeholder for lyrics
    That would normally come from Genius
    But since we couldn't find them there
    Gemini would provide them in real use

    [Chorus]
    These are mock lyrics for "{title}"
    By the artist known as "{artist}"
    In production, we'd use Gemini
    To get the actual song lyrics
    
    [Verse 2]
    The real implementation would
    Connect to Google's powerful AI
    To retrieve accurate lyrics
    When Genius API falls short
    """
    
    return {
        "status": "success",
        "title": title,
        "artist": artist,
        "lyrics": mock_lyrics_text.strip(),
        "note": "These are mock lyrics for development",
        "api_used": "mock_data"
    }

def mock_translate_lyrics(lyrics: str, target_lang: str) -> Dict[str, Any]:
    """Mock translation function for development and testing."""
    logger.info(f"Using mock translation for target language: {target_lang}")
    
    if target_lang.lower() == "spanish":
        mock_translation = """
        Esto es una traducción simulada
        Para propósitos de desarrollo
        
        Las letras reales serían traducidas
        Por la API de Gemini en producción
        """
    else:
        mock_translation = """
        Ceci est une traduction simulée
        À des fins de développement
        
        Les paroles réelles seraient traduites
        Par l'API Gemini en production
        """
    
    return {
        "status": "success",
        "original_lyrics": lyrics,
        "translated_lyrics": mock_translation.strip(),
        "source_language": "English",
        "target_language": target_lang,
        "note": "This is a mock translation for development",
        "api_used": "mock_data"
    }

def mock_explain_song_meaning(title: str, artist: str) -> Dict[str, Any]:
    """Mock song meaning analysis for development and testing."""
    logger.info(f"Using mock song explanation for '{title}' by '{artist}'")
    
    mock_meaning = f"""
    # Analysis of "{title}" by {artist}
    
    ## Main Theme
    This song explores themes of love, loss, and personal growth. It uses powerful imagery to convey the emotional journey of the protagonist.
    
    ## Cultural Context
    Released during a time of significant social change, this song reflects the broader cultural shifts of its era. It resonated with audiences due to its authentic emotional expression.
    
    ## Hidden Meanings
    The recurring metaphors of natural elements (water, fire, earth) represent the cycle of emotional transformation. The chorus symbolizes rebirth and renewal after a period of difficulty.
    
    ## Emotional Impact
    The song creates a cathartic experience, allowing listeners to process their own feelings of loss while offering a sense of hope and resilience. Its emotional resonance is enhanced by the vocal delivery and instrumental arrangement.
    """
    
    return {
        "status": "success",
        "title": title,
        "artist": artist,
        "meaning": mock_meaning.strip(),
        "note": "This is a mock analysis for development",
        "api_used": "mock_data"
    }

def mock_similar_songs(title: str, artist: str) -> Dict[str, Any]:
    """Mock similar songs recommendation for development and testing."""
    logger.info(f"Using mock song recommendations for '{title}' by '{artist}'")
    
    mock_recommendations = [
        {
            "title": "Bohemian Rhapsody",
            "artist": "Queen",
            "reason": "Epic composition with emotional depth and innovative structure",
            "year": "1975"
        },
        {
            "title": "November Rain",
            "artist": "Guns N' Roses",
            "reason": "Sweeping ballad with orchestral elements and emotional build",
            "year": "1991"
        },
        {
            "title": "Stairway to Heaven",
            "artist": "Led Zeppelin",
            "reason": "Progressive structure with philosophical lyrics and instrumental brilliance",
            "year": "1971"
        },
        {
            "title": "A Day in the Life",
            "artist": "The Beatles",
            "reason": "Experimental song structure with contrasting sections and orchestral climax",
            "year": "1967"
        },
        {
            "title": "Comfortably Numb",
            "artist": "Pink Floyd",
            "reason": "Atmospheric production with emotional vocals and legendary guitar work",
            "year": "1979"
        }
    ]
    
    return {
        "status": "success",
        "title": title,
        "artist": artist,
        "recommendations": mock_recommendations,
        "note": "These are mock recommendations for development",
        "api_used": "mock_data"
    } 