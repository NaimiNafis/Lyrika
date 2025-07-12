/**
 * Lyrika - Background Script
 * Handles audio capture and communication with the server
 */

// Configuration
const API_BASE_URL = 'http://localhost:5001/api'; // Update this with your server URL

/**
 * Listen for messages from popup
 */
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('Background script received message:', request);

  if (request.action === 'startListening') {
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
      if (!tabs || !tabs[0]) {
        sendResponse({ status: 'error', message: 'No active tab found' });
        return;
      }
      
      console.log('Getting media stream ID for tab:', tabs[0].id);
      
      chrome.tabCapture.getMediaStreamId(
        {targetTabId: tabs[0].id},
        function(streamId) {
          console.log('Media stream ID obtained:', streamId);
          sendResponse({ status: 'success', streamId: streamId });
        }
      );
    });
    return true; // Will respond asynchronously
  }

  if (request.action === 'sendAudioToServer') {
    console.log('Received audio data from popup, sending to server');
    sendAudioToServer(request.audioData)
      .then(result => sendResponse(result))
      .catch(error => sendResponse({ status: 'error', message: error.message }));
    return true;
  }

  if (request.action === 'manualSearch') {
    searchLyrics(request.songTitle, request.artist)
      .then(result => sendResponse(result))
      .catch(error => sendResponse({ status: 'error', message: error.message }));
    return true; // Will respond asynchronously
  }
});

/**
 * Send audio data to server for identification
 */
async function sendAudioToServer(audioData) {
  try {
    console.log('Sending audio data to server...');
    
    const response = await fetch(`${API_BASE_URL}/identify`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ audio_data: audioData })
    });

    if (!response.ok) {
      throw new Error(`Server returned ${response.status}: ${response.statusText}`);
    }

    const result = await response.json();
    console.log('Server response:', result);
    return result;
  } catch (error) {
    console.error('Error sending audio to server:', error);
    throw new Error('Failed to communicate with the Lyrika server. Please check your connection.');
  }
}

/**
 * Search for lyrics using song title and artist
 */
async function searchLyrics(songTitle, artist) {
  try {
    const url = new URL(`${API_BASE_URL}/lyrics`);
    url.searchParams.append('title', songTitle);
    if (artist) {
      url.searchParams.append('artist', artist);
    }
    
    const response = await fetch(url.toString());
    
    if (!response.ok) {
      throw new Error(`Server returned ${response.status}: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error in searchLyrics:', error);
    throw error;
  }
} 