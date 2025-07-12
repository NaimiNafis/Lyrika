#!/usr/bin/env python3
"""
Test script for song meaning analysis
"""

import os
import logging
from dotenv import load_dotenv
import google.generativeai as genai
from api.gemini import explain_song_meaning, is_configured, GEMINI_API_KEY

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('song_meaning_test')

# Load environment variables
print("Loading environment variables...")
load_dotenv()
print(f"Environment variables loaded. GEMINI_API_KEY exists in os.environ: {'GEMINI_API_KEY' in os.environ}")
print(f"GEMINI_API_KEY from module: {'Present' if GEMINI_API_KEY else 'Missing'}")
if GEMINI_API_KEY:
    print(f"GEMINI_API_KEY length: {len(GEMINI_API_KEY)}, starts with: {GEMINI_API_KEY[:4]}...")

# Manually configure Gemini API
if 'GEMINI_API_KEY' in os.environ:
    api_key = os.environ['GEMINI_API_KEY']
    print(f"Manually configuring Gemini API with key from os.environ (starts with {api_key[:4]}...)")
    genai.configure(api_key=api_key)

def test_song_meaning():
    """Test the song meaning explanation function"""
    # Check if Gemini API is configured
    api_configured = is_configured()
    print(f"Gemini API configured according to is_configured(): {api_configured}")
    
    if not api_configured:
        logger.error("Gemini API is not configured")
        return False
    
    # Test data
    title = "Imagine"
    artist = "John Lennon"
    lyrics = """
    Imagine there's no heaven
    It's easy if you try
    No hell below us
    Above us, only sky
    Imagine all the people
    Livin' for today
    
    Imagine there's no countries
    It isn't hard to do
    Nothing to kill or die for
    And no religion, too
    Imagine all the people
    Livin' life in peace
    
    You may say I'm a dreamer
    But I'm not the only one
    I hope someday you'll join us
    And the world will be as one
    """
    
    # Call the function
    logger.info(f"Testing song meaning analysis for '{title}' by '{artist}'")
    result = explain_song_meaning(title, artist, lyrics)
    
    # Check result
    if result["status"] == "success":
        logger.info("Song meaning analysis successful!")
        logger.info(f"API used: {result.get('api_used', 'unknown')}")
        logger.info("First 100 characters of analysis:")
        logger.info(result["meaning"][:100] + "...")
        return True
    else:
        logger.error(f"Song meaning analysis failed: {result.get('message', 'Unknown error')}")
        logger.error(f"API used: {result.get('api_used', 'unknown')}")
        return False

if __name__ == "__main__":
    print("\n=== Song Meaning Analysis Test ===\n")
    success = test_song_meaning()
    print(f"\nTest {'PASSED' if success else 'FAILED'}\n") 