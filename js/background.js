/**
 * Lyrika - Background Script
 * Handles audio capture and recognition using ACRCloud API
 */

// Import API clients
import { identifySong } from './api/acrcloud-client.js';

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

    // Start audio capture
    console.log('Starting audio capture for tab:', tab.id);
    
    // Placeholder for actual implementation
    // In a real implementation, this would use chrome.tabCapture.capture
    // to get the audio stream from the tab
    
    // Mock response for development
    return {
      status: 'success',
      title: 'Sample Song',
      artist: 'Sample Artist',
      lyrics: 'This is a placeholder for song lyrics.\n\nIt will be replaced with actual lyrics from the Genius API in the final implementation.',
      youtubeId: 'dQw4w9WgXcQ'
    };
    
  } catch (error) {
    console.error('Error in startRecognition:', error);
    throw error;
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
    // Placeholder for actual implementation
    // In a real implementation, this would call the Genius API
    
    return {
      status: 'success',
      title: songTitle,
      artist: artist,
      lyrics: `This is a placeholder for lyrics of "${songTitle}" by ${artist}.\n\nIt will be replaced with actual lyrics from the Genius API in the final implementation.`,
      youtubeId: null
    };
  } catch (error) {
    console.error('Error in searchLyrics:', error);
    throw error;
  }
} 