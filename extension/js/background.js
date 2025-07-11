/**
 * Lyrika - Background Script
 * Handles audio capture and communication with the server
 */

// Configuration
const API_BASE_URL = 'http://localhost:5000/api'; // Update this with your server URL

// Global variables
let mediaRecorder;
let audioChunks = [];
let tabCaptureStream;

/**
 * Listen for messages from popup
 */
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('Background script received message:', request);

  if (request.action === 'startListening') {
    startRecognition()
      .then(result => sendResponse(result))
      .catch(error => sendResponse({ status: 'error', message: error.message }));
    return true; // Will respond asynchronously
  }

  if (request.action === 'stopListening') {
    stopRecording();
    sendResponse({ status: 'success', message: 'Recording stopped' });
    return false;
  }

  if (request.action === 'manualSearch') {
    searchLyrics(request.songTitle, request.artist)
      .then(result => sendResponse(result))
      .catch(error => sendResponse({ status: 'error', message: error.message }));
    return true; // Will respond asynchronously
  }
});

/**
 * Start capturing audio from the active tab
 */
async function startRecognition() {
  try {
    // Get current active tab
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab) {
      throw new Error('No active tab found');
    }

    console.log('Starting audio capture for tab:', tab.id);

    // Start audio capture
    const stream = await chrome.tabCapture.capture({
      audio: true,
      video: false,
      audioConstraints: {
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true
      }
    });

    if (!stream) {
      throw new Error('Could not capture tab audio. Please ensure you have the correct permissions.');
    }

    tabCaptureStream = stream;

    // Set up MediaRecorder to capture audio
    const audioCtx = new AudioContext();
    const source = audioCtx.createMediaStreamSource(stream);
    const dest = audioCtx.createMediaStreamDestination();
    source.connect(dest);

    // Create and configure recorder
    mediaRecorder = new MediaRecorder(dest.stream, { mimeType: 'audio/webm' });
    audioChunks = [];

    // Listen for data
    mediaRecorder.ondataavailable = (event) => {
      audioChunks.push(event.data);
    };

    // When recording is complete, send to server
    mediaRecorder.onstop = async () => {
      try {
        // Create audio blob from chunks
        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
        
        // Convert blob to base64
        const base64Data = await blobToBase64(audioBlob);
        
        // Send to server
        const result = await sendAudioToServer(base64Data);
        
        // Clean up
        stopRecording();
        
        return result;
      } catch (error) {
        console.error('Error processing audio:', error);
        throw error;
      }
    };

    // Start recording
    mediaRecorder.start();

    // Record for 10 seconds then stop
    setTimeout(() => {
      if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
      }
    }, 10000);

    // For testing, immediately return mock data instead of waiting
    return await mockServerResponse();

  } catch (error) {
    console.error('Error in startRecognition:', error);
    throw error;
  }
}

/**
 * Convert Blob to Base64
 */
function blobToBase64(blob) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => {
      // Extract the base64 data part (remove data:audio/webm;base64, prefix)
      const base64 = reader.result.split(',')[1];
      resolve(base64);
    };
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
}

/**
 * Send audio data to server for identification
 */
async function sendAudioToServer(audioData) {
  try {
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

    return await response.json();
  } catch (error) {
    console.error('Error sending audio to server:', error);
    throw new Error('Failed to communicate with the Lyrika server. Please check your connection.');
  }
}

/**
 * Stop recording audio
 */
function stopRecording() {
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop();
  }
  
  if (tabCaptureStream) {
    tabCaptureStream.getTracks().forEach(track => track.stop());
    tabCaptureStream = null;
  }
  
  audioChunks = [];
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

/**
 * Mock server response for testing
 */
async function mockServerResponse() {
  // Simulate server delay
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  return {
    status: 'success',
    title: 'Bohemian Rhapsody',
    artist: 'Queen',
    lyrics: `Is this the real life? Is this just fantasy?
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
Carry on, carry on as if nothing really matters`,
    youtubeId: 'fJ9rUzIMcZQ'
  };
} 