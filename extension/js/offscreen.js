/**
 * Lyrika - Offscreen Script
 * Handles audio capture in a persistent context
 */

let mediaRecorder;
let audioChunks = [];
let tabCaptureStream;

// Listen for messages from the service worker
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'startCapture') {
    startCapture(message.tabId)
      .then(() => sendResponse({ status: 'success' }))
      .catch(error => sendResponse({ status: 'error', message: error.message }));
    return true;
  }

  if (message.action === 'stopCapture') {
    stopCapture()
      .then(base64Data => sendResponse({ status: 'success', audioData: base64Data }))
      .catch(error => sendResponse({ status: 'error', message: error.message }));
    return true;
  }
});

/**
 * Start capturing audio from the specified tab
 */
async function startCapture(tabId) {
  try {
    console.log('Starting capture in offscreen document for tab:', tabId);
    
    // Get audio stream
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
      throw new Error('Failed to capture tab audio');
    }
    
    tabCaptureStream = stream;
    
    // Create a MediaRecorder instance
    mediaRecorder = new MediaRecorder(stream);
    audioChunks = [];
    
    // Listen for data
    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        audioChunks.push(event.data);
      }
    };
    
    // Start recording
    mediaRecorder.start();
    
    // Notify service worker that recording has started
    chrome.runtime.sendMessage({ action: 'captureStarted' });
  } catch (error) {
    console.error('Error starting capture:', error);
    throw error;
  }
}

/**
 * Stop capturing audio and return the base64 encoded data
 */
async function stopCapture() {
  return new Promise((resolve, reject) => {
    try {
      if (!mediaRecorder || mediaRecorder.state === 'inactive') {
        reject(new Error('No active recording'));
        return;
      }
      
      // When recording is stopped, process the audio data
      mediaRecorder.onstop = async () => {
        try {
          // Create a single blob from all audio chunks
          const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
          
          // Convert to base64
          const base64Data = await blobToBase64(audioBlob);
          
          // Clean up
          cleanup();
          
          resolve(base64Data);
        } catch (error) {
          reject(error);
        }
      };
      
      // Stop recording
      mediaRecorder.stop();
      
    } catch (error) {
      cleanup();
      reject(error);
    }
  });
}

/**
 * Clean up resources
 */
function cleanup() {
  if (tabCaptureStream) {
    tabCaptureStream.getTracks().forEach(track => track.stop());
    tabCaptureStream = null;
  }
  
  mediaRecorder = null;
  audioChunks = [];
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