/**
 * Lyrika - Popup Script
 * Handles UI interactions and communication with background script
 */

// DOM elements
const initialState = document.getElementById('initial-state');
const listeningState = document.getElementById('listening-state');
const resultsState = document.getElementById('results-state');
const errorState = document.getElementById('error-state');
const manualInput = document.getElementById('manual-input');

const startListeningBtn = document.getElementById('start-listening');
const tryAgainBtn = document.getElementById('try-again');
const backButton = document.getElementById('back-button');
const manualSearchBtn = document.getElementById('manual-search');

const songTitleElem = document.getElementById('song-title');
const artistElem = document.getElementById('artist');
const lyricsElem = document.getElementById('lyrics');
const errorMessageElem = document.getElementById('error-message');
const youtubeLink = document.getElementById('youtube-link');

// Timers
let manualFallbackTimer;
let isProcessing = false;

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
  // Add event listeners to buttons
  startListeningBtn.addEventListener('click', debounce(startListening, 300));
  tryAgainBtn.addEventListener('click', resetToInitialState);
  backButton.addEventListener('click', resetToInitialState);
  manualSearchBtn.addEventListener('click', handleManualSearch);
  
  // Add click to copy functionality
  songTitleElem.addEventListener('click', copySongInfo);
});

/**
 * Start listening for audio and identify the song
 */
function startListening() {
  if (isProcessing) {
    console.log('Already processing audio');
    return;
  }
  
  isProcessing = true;
  showState(listeningState);
  clearTimeout(manualFallbackTimer);
  
  // Show manual input after 10 seconds if no result
  manualFallbackTimer = setTimeout(() => {
    manualInput.classList.remove('hidden');
  }, 10000);
  
  // Send message to background script
  chrome.runtime.sendMessage({ action: 'startListening' }, handleResponse);
}

/**
 * Handle response from background script
 */
function handleResponse(response) {
  clearTimeout(manualFallbackTimer);
  isProcessing = false;
  
  console.log('Received response:', response);
  
  if (response.status === 'success') {
    displayResults(response);
  } else {
    displayError(response.message);
  }
}

/**
 * Display successful results
 */
function displayResults(data) {
  // Populate UI elements with data
  songTitleElem.textContent = data.title;
  artistElem.textContent = data.artist;
  
  // Handle lyrics
  if (data.lyrics && data.lyrics.trim()) {
    lyricsElem.textContent = data.lyrics;
  } else {
    lyricsElem.textContent = 'This appears to be an instrumental track.';
  }
  
  // Handle YouTube link
  if (data.youtubeId) {
    youtubeLink.href = `https://www.youtube.com/watch?v=${data.youtubeId}`;
    youtubeLink.classList.remove('hidden');
  } else {
    youtubeLink.classList.add('hidden');
  }
  
  // Show results state
  showState(resultsState);
}

/**
 * Display error message
 */
function displayError(message) {
  errorMessageElem.textContent = message || "Couldn't identify the song. Please try again.";
  showState(errorState);
  manualInput.classList.remove('hidden');
}

/**
 * Reset to initial state
 */
function resetToInitialState() {
  showState(initialState);
  manualInput.classList.add('hidden');
  
  // Clear previous data
  songTitleElem.textContent = '';
  artistElem.textContent = '';
  lyricsElem.textContent = '';
  youtubeLink.classList.add('hidden');
  
  // Clear any copied state
  songTitleElem.dataset.copied = false;
}

/**
 * Handle manual search
 */
function handleManualSearch() {
  const songTitle = document.getElementById('manual-song').value.trim();
  const artist = document.getElementById('manual-artist').value.trim();
  
  if (!songTitle) {
    alert('Please enter a song title');
    return;
  }
  
  showState(listeningState);
  
  chrome.runtime.sendMessage({
    action: 'manualSearch',
    songTitle: songTitle,
    artist: artist
  }, handleResponse);
}

/**
 * Copy song info to clipboard
 */
function copySongInfo() {
  const songInfo = `${songTitleElem.textContent} by ${artistElem.textContent}`;
  
  navigator.clipboard.writeText(songInfo)
    .then(() => {
      // Show "Copied!" feedback
      songTitleElem.dataset.copied = true;
      setTimeout(() => {
        songTitleElem.dataset.copied = false;
      }, 2000);
    })
    .catch(err => {
      console.error('Could not copy text:', err);
    });
}

/**
 * Show a specific state and hide others
 */
function showState(stateToShow) {
  // Hide all states
  initialState.classList.add('hidden');
  listeningState.classList.add('hidden');
  resultsState.classList.add('hidden');
  errorState.classList.add('hidden');
  
  // Show the requested state
  stateToShow.classList.remove('hidden');
}

/**
 * Debounce function to prevent multiple rapid clicks
 */
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
} 