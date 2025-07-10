#!/bin/bash

# Lyrika Extension Packaging Script

# Ensure we're in the project root
cd "$(dirname "$0")"

echo "Packaging Lyrika extension..."

# Create build directory
mkdir -p build

# Copy necessary files
echo "Copying files..."
cp -r manifest.json popup.html build/
mkdir -p build/css
cp -r css/* build/css/
mkdir -p build/js/api
cp -r js/background.js js/popup.js build/js/
cp -r js/api/acrcloud-client.js js/api/shazam-client.js build/js/api/

# Copy config files if they exist
if [ -f "js/api/acrcloud-config.js" ]; then
  cp js/api/acrcloud-config.js build/js/api/
  echo "Included ACRCloud config."
else
  echo "Warning: ACRCloud config not found. Run 'node build-config.js' first."
fi

if [ -f "js/api/genius-config.js" ]; then
  cp js/api/genius-config.js build/js/api/
  echo "Included Genius config."
else
  echo "Warning: Genius config not found. Run 'node build-config.js' first."
fi

# Create icons directory
mkdir -p build/assets/icons

# Use placeholder icons if actual icons don't exist
if [ ! -f "assets/icons/icon16.png" ]; then
  echo "Warning: Icons not found. Using placeholders."
  # Create placeholder directory in case it doesn't exist
  mkdir -p assets/icons
  
  # Use echo to create a minimal 1x1 pixel data URI for each icon size
  # This is just a temporary placeholder until real icons are added
  echo "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==" > assets/icons/icon16.png
  echo "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==" > assets/icons/icon48.png
  echo "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==" > assets/icons/icon128.png
fi

# Copy icons
cp -r assets/icons/* build/assets/icons/

# Remove development/test files
rm -rf build/js/test.js
rm -rf build/assets/test-audio

# Create zip file for Chrome Web Store
echo "Creating ZIP file..."
cd build
zip -r ../lyrika-extension.zip *

echo "Extension packaged to lyrika-extension.zip"
echo "You can load it in Chrome by going to chrome://extensions, enabling Developer Mode, and clicking 'Load unpacked' to select the 'build' directory." 