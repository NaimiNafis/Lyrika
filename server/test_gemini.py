#!/usr/bin/env python3
"""
Test script for Gemini API
"""

import os
import logging
from dotenv import load_dotenv
import google.generativeai as genai

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('gemini_test')

# Load environment variables
print("Loading environment variables...")
load_dotenv()
print(f"Environment variables loaded. GEMINI_API_KEY exists: {'GEMINI_API_KEY' in os.environ}")

def test_gemini_api():
    """Test if the Gemini API key works"""
    try:
        # Get API key from environment
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            logger.error("GEMINI_API_KEY not found in environment variables")
            return False
        
        logger.info(f"API key found (length: {len(api_key)}, starts with: {api_key[:4]}...)")
        
        # Configure the API
        genai.configure(api_key=api_key)
        
        # Test with a simple prompt
        logger.info("Testing API with a simple prompt...")
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content("Say hello in one word")
        
        if response and response.text:
            logger.info(f"API test successful! Response: {response.text.strip()}")
            return True
        else:
            logger.error("API returned empty response")
            return False
            
    except Exception as e:
        logger.exception(f"Error testing Gemini API: {str(e)}")
        return False

if __name__ == "__main__":
    print("\n=== Gemini API Test ===\n")
    
    # Print all environment variables (excluding actual values)
    print("Environment variables:")
    for key in sorted(os.environ.keys()):
        if key.startswith("GEMINI"):
            print(f"  {key}: {os.environ[key][:4]}... (length: {len(os.environ[key])})")
    print()
    
    success = test_gemini_api()
    print(f"\nTest {'PASSED' if success else 'FAILED'}\n") 