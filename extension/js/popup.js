/**
 * Lyrika - Popup Script
 * Handles UI interactions and communication with background script
 */

// DOM elements
const initialState = document.getElementById('initial-state');
const listeningState = document.getElementById('listening-state');
const resultsState = document.getElementById('results-state');
const errorState = document.getElementById('error-state');
const searchTab = document.getElementById('search-tab');

const startListeningBtn = document.getElementById('start-listening');
const tryAgainBtn = document.getElementById('try-again');
const backButton = document.getElementById('back-button');
const manualSearchBtn = document.getElementById('manual-search');

const songTitleElem = document.getElementById('song-title');
const artistElem = document.getElementById('artist');
const lyricsElem = document.getElementById('lyrics');
const errorMessageElem = document.getElementById('error-message');
const albumArtworkElem = document.getElementById('album-artwork');
const youtubeLink = document.getElementById('youtube-link');
const spotifyLink = document.getElementById('spotify-link');
const appleMusicLink = document.getElementById('apple-music-link');

// Enhancement elements
const translateOptions = document.querySelectorAll('.translate-option');
const getRecommendationsBtn = document.getElementById('get-recommendations');

const lyricsLoadingElem = document.getElementById('lyrics-loading');
const recommendationsListElem = document.getElementById('recommendations-list');
const recommendationsLoadingElem = document.getElementById('recommendations-loading');
const searchLoadingElem = document.getElementById('search-loading');

// Timers and state
let manualFallbackTimer;
let isProcessing = false;
let mediaRecorder = null;
let audioChunks = [];
let currentSongData = null;
let originalLyrics = '';

// API base URL
const API_BASE_URL = 'http://localhost:5001/api';

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
  // Add event listeners to buttons
  startListeningBtn.addEventListener('click', debounce(startListening, 300));
  tryAgainBtn.addEventListener('click', resetToInitialState);
  backButton.addEventListener('click', resetToInitialState);
  manualSearchBtn.addEventListener('click', handleManualSearch);
  
  // Add click to copy functionality
  songTitleElem.addEventListener('click', copySongInfo);

  // Add event listeners for links
  youtubeLink.addEventListener('click', openYoutubeLink);
  spotifyLink.addEventListener('click', openSpotifyLink);
  appleMusicLink.addEventListener('click', openAppleMusicLink);
  
  // Add event listeners for enhancements
  translateOptions.forEach(option => {
    option.addEventListener('click', handleTranslateOption);
  });
  
  // Load saved state if available
  restoreState();
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
  
  // Show search tab after 7 seconds if no result
  manualFallbackTimer = setTimeout(() => {
    // Switch to search tab if identification takes too long
    const searchTabElement = document.getElementById('search-tab');
    if (searchTabElement) {
      searchTabElement.click();
    }
  }, 7000);
  
  // Get streamId from background script
  chrome.runtime.sendMessage({ action: 'startListening' }, async (response) => {
    console.log('Received streamId response:', response);
    
    if (response.status === 'error' || !response.streamId) {
      displayError(response.message || "Couldn't access tab audio");
      return;
    }
    
    try {
      // Use the streamId to create a MediaStream
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          mandatory: {
            chromeMediaSource: 'tab',
            chromeMediaSourceId: response.streamId
          }
        },
        video: false
      });
      
      // Start recording
      captureAudio(stream);
    } catch (error) {
      console.error('Error capturing audio:', error);
      displayError("Couldn't capture audio: " + error.message);
    }
  });
}

/**
 * Capture audio using the MediaRecorder API
 */
function captureAudio(stream) {
  try {
    // Create audio context and connect nodes
    const audioCtx = new AudioContext();
    const source = audioCtx.createMediaStreamSource(stream);
    const dest = audioCtx.createMediaStreamDestination();
    source.connect(dest);
    
    // Set up MediaRecorder
    mediaRecorder = new MediaRecorder(dest.stream);
    audioChunks = [];
    
    // Handle data availability
    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        audioChunks.push(event.data);
      }
    };
    
    // When recording stops
    mediaRecorder.onstop = async () => {
      try {
        // Create blob from chunks
        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
        
        // Convert to base64
        const base64Data = await blobToBase64(audioBlob);
        
        console.log('Audio captured successfully, sending to server...');
        
        // Stop all tracks
        stream.getTracks().forEach(track => track.stop());
        
        // Send to background for processing
        chrome.runtime.sendMessage({ 
          action: 'sendAudioToServer', 
          audioData: base64Data 
        }, handleResponse);
      } catch (error) {
        console.error('Error processing audio:', error);
        displayError('Error processing audio: ' + error.message);
      }
    };
    
    // Start recording
    mediaRecorder.start();
    
    // Record for 5 seconds
    setTimeout(() => {
      if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
      }
    }, 5000);
  } catch (error) {
    console.error('Error setting up audio recording:', error);
    displayError('Error setting up audio recording: ' + error.message);
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
    // Automatically switch to search tab on error
    const searchTabElement = document.getElementById('search-tab');
    if (searchTabElement) {
      searchTabElement.click();
    }
  }
}

/**
 * Format lyrics text to ensure consistent display
 * @param {string} lyrics - Raw lyrics text
 * @returns {string} - Formatted lyrics text
 */
function formatLyrics(lyrics) {
  if (!lyrics || !lyrics.trim()) {
    return '';
  }
  
  let formattedLyrics = lyrics.trim();
  
  // Remove any metadata or headers
  formattedLyrics = formattedLyrics.replace(/^.*?(Lyrics|lyrics).*?$/m, '');
  formattedLyrics = formattedLyrics.replace(/^.*?Contributors.*?$/m, '');
  
  // 1. Join words broken across lines (lowercase to lowercase)
  formattedLyrics = formattedLyrics.replace(/([a-z])[\s]*\n[\s]*([a-z])/g, '$1 $2');
  
  // 2. Ensure proper spacing around punctuation
  formattedLyrics = formattedLyrics.replace(/([.,;:!?])[\s]*\n/g, '$1\n');
  
  // 3. Preserve intentional line breaks in song lyrics (after punctuation, etc.)
  formattedLyrics = formattedLyrics.replace(/([.,;:!?])[\s]*([A-Z])/g, '$1\n$2');
  
  // 4. Ensure consistent spacing
  formattedLyrics = formattedLyrics.replace(/[ \t]+/g, ' ');
  
  // 5. Normalize line endings
  formattedLyrics = formattedLyrics.replace(/\r\n/g, '\n');
  
  // 6. Remove excess blank lines but preserve verse structure
  formattedLyrics = formattedLyrics.replace(/\n{3,}/g, '\n\n');
  
  return formattedLyrics;
}

/**
 * Display successful results
 */
function displayResults(data) {
  // Store current song data for enhancements
  currentSongData = data;
  
  // Populate UI elements with data
  songTitleElem.textContent = data.title;
  artistElem.textContent = data.artist;
  
  // Handle lyrics
  if (data.lyrics && data.lyrics.trim()) {
    // Format lyrics using the shared formatting function
    let cleanLyrics = formatLyrics(data.lyrics);
    
    // Store original lyrics for translation comparison
    originalLyrics = cleanLyrics;
    
    lyricsElem.textContent = cleanLyrics;
    
    // Add scrolling to the lyrics container if content is long
    const lyricsContainer = document.querySelector('.lyrics-container');
    if (lyricsContainer && cleanLyrics.split('\n').length > 10) {
      lyricsContainer.classList.add('scrollable');
    }
    
    // Reset enhancement UI
    resetEnhancementUI();
  } else {
    lyricsElem.textContent = 'This appears to be an instrumental track.';
  }
  
  // Handle album artwork
  if (data.albumArtwork) {
    // Use album artwork from the API response if available
    albumArtworkElem.src = data.albumArtwork;
    console.log('Using album artwork from API:', data.albumArtwork);
  } else {
    // Fetch album artwork if not provided in the response
  fetchAlbumArtwork(data.title, data.artist);
  }
  
  // Handle platform links
  if (data.youtubeId) {
    youtubeLink.href = `https://www.youtube.com/watch?v=${data.youtubeId}`;
    youtubeLink.classList.remove('hidden');
  } else {
    youtubeLink.classList.add('hidden');
  }

  if (data.spotifyId) {
    spotifyLink.href = `https://open.spotify.com/track/${data.spotifyId}`;
    spotifyLink.classList.remove('hidden');
  } else {
    spotifyLink.classList.add('hidden');
  }
  
  // Handle Apple Music link - using iTunes search for Apple Music URLs
  const appleSearch = encodeURIComponent(`${data.title} ${data.artist}`);
  appleMusicLink.href = `https://music.apple.com/search?term=${appleSearch}`;
  // Only show Apple Music link if we have a title and artist
  if (data.title && data.artist) {
    appleMusicLink.classList.remove('hidden');
  } else {
  appleMusicLink.classList.add('hidden');
  }
  
  // Show results state
  showState(resultsState);
  
  // Save state to storage
  saveState({
    state: 'results',
    songData: {
      title: data.title,
      artist: data.artist,
      lyrics: originalLyrics,
      youtubeId: data.youtubeId || '',
      spotifyId: data.spotifyId || '',
      albumArtworkSrc: albumArtworkElem.src
    }
  });
}

/**
 * Save current state to Chrome storage
 */
function saveState(stateData) {
  chrome.storage.local.set({ 'lyrikaState': stateData }, function() {
    console.log('State saved:', stateData);
  });
}

/**
 * Restore state from Chrome storage
 */
function restoreState() {
  chrome.storage.local.get(['lyrikaState'], function(result) {
    if (result.lyrikaState) {
      const savedState = result.lyrikaState;
      console.log('Restoring state:', savedState);
      
      if (savedState.state === 'results' && savedState.songData) {
        // Restore song data
        const songData = savedState.songData;
        
        // Format the stored lyrics using the shared formatting function
        const formattedLyrics = formatLyrics(songData.lyrics);
        
        // Set current song data
        currentSongData = {
          title: songData.title,
          artist: songData.artist,
          lyrics: formattedLyrics,
          youtubeId: songData.youtubeId,
          spotifyId: songData.spotifyId
        };
        
        // Populate UI elements
        songTitleElem.textContent = songData.title;
        artistElem.textContent = songData.artist;
        originalLyrics = formattedLyrics;
        lyricsElem.textContent = formattedLyrics;
        
        // Restore album artwork if available
        if (songData.albumArtworkSrc) {
          albumArtworkElem.src = songData.albumArtworkSrc;
        }
        
        // Restore platform links
        if (songData.youtubeId) {
          youtubeLink.href = `https://www.youtube.com/watch?v=${songData.youtubeId}`;
          youtubeLink.classList.remove('hidden');
        }
        
        if (songData.spotifyId) {
          spotifyLink.href = `https://open.spotify.com/track/${songData.spotifyId}`;
          spotifyLink.classList.remove('hidden');
        }
        
        // Set Apple Music link
        const appleSearch = encodeURIComponent(`${songData.title} ${songData.artist}`);
        appleMusicLink.href = `https://music.apple.com/search?term=${appleSearch}`;
        if (songData.title && songData.artist) {
          appleMusicLink.classList.remove('hidden');
        }
        
        // Show results state
        showState(resultsState);
        
        // Add event listener for the get recommendations button
        document.getElementById('get-recommendations')?.addEventListener('click', handleGetRecommendations);
      }
    }
  });
}

/**
 * Fetch album artwork using the song title and artist
 */
async function fetchAlbumArtwork(title, artist) {
  try {
    // Set a loading state with default artwork
    albumArtworkElem.src = 'assets/icons/icon128.png';
    
    // Try multiple sources to get the best album artwork
    
    // Source 1: Check if we have spotifyId - but use a CORS-friendly approach
    if (currentSongData && currentSongData.spotifyId) {
      const spotifyId = currentSongData.spotifyId;
      // Instead of fetching the embed page (which causes CORS issues),
      // try using the direct Spotify image URL pattern if we have a spotifyId
      // Format: https://i.scdn.co/image/{imageId}
      
      // We'll rely on the Last.fm and other APIs below instead of
      // attempting to fetch from Spotify directly
    }
      
    // Source 2: Last.fm API (public API, no key needed for basic info)
    try {
      const lastFmUrl = `https://ws.audioscrobbler.com/2.0/?method=track.getInfo&api_key=12dec50804977a8d15e406a4b6d7f250&artist=${encodeURIComponent(artist)}&track=${encodeURIComponent(title)}&format=json`;
      
      const response = await fetch(lastFmUrl);
      const data = await response.json();
      
          if (data && data.track && data.track.album && data.track.album.image) {
            // Get the largest image (last in the array)
            const images = data.track.album.image;
            const largeImage = images.find(img => img.size === 'extralarge') || 
                              images.find(img => img.size === 'large') ||
                              images[images.length - 1];
            
        if (largeImage && largeImage['#text'] && largeImage['#text'].length > 10) {
              albumArtworkElem.src = largeImage['#text'];
          saveAlbumArtwork(largeImage['#text']);
          return;
        }
      }
    } catch (error) {
      console.log('Error fetching Last.fm artwork:', error);
      // Continue to next source
    }
    
    // Source 3: iTunes/Apple Music Search API (no auth required)
    try {
      const itunesUrl = `https://itunes.apple.com/search?term=${encodeURIComponent(`${title} ${artist}`)}&entity=song&limit=1`;
      
      const response = await fetch(itunesUrl);
      const data = await response.json();
      
      if (data && data.results && data.results.length > 0) {
        // Get the artwork URL and modify it to get higher resolution
        let artworkUrl = data.results[0].artworkUrl100;
        // Replace 100x100 with 600x600 for higher resolution
        artworkUrl = artworkUrl.replace('100x100bb', '600x600bb');
        
        albumArtworkElem.src = artworkUrl;
        saveAlbumArtwork(artworkUrl);
        return;
      }
    } catch (error) {
      console.log('Error fetching iTunes artwork:', error);
      // Fall back to default icon
    }
    
    // Source 4: MusicBrainz + Cover Art Archive API
    // Note: This comes last because it's often slower than the others
    try {
      // First search for the release by artist and title
      const mbUrl = `https://musicbrainz.org/ws/2/release?query=artist:${encodeURIComponent(artist)}%20AND%20release:${encodeURIComponent(title)}&fmt=json`;
      
      const mbResponse = await fetch(mbUrl);
      const mbData = await mbResponse.json();
      
      if (mbData && mbData.releases && mbData.releases.length > 0) {
        const releaseId = mbData.releases[0].id;
        
        // Then get artwork from Cover Art Archive using the release ID
        const artworkUrl = `https://coverartarchive.org/release/${releaseId}/front`;
        
        // This is a redirect URL that leads to the actual image
        const checkResponse = await fetch(artworkUrl, { method: 'HEAD' });
        
        if (checkResponse.ok) {
          albumArtworkElem.src = artworkUrl;
          saveAlbumArtwork(artworkUrl);
          return;
        }
      }
    } catch (error) {
      console.log('Error fetching MusicBrainz/Cover Art Archive artwork:', error);
      // Fall back to default icon
    }
    
    // If all sources fail, keep the default icon
    console.log('No album artwork found for', title, 'by', artist);
    
  } catch (error) {
    console.error('Error setting album artwork:', error);
    // Fallback to default icon
    albumArtworkElem.src = 'assets/icons/icon128.png';
  }
}

/**
 * Save album artwork URL to storage
 */
function saveAlbumArtwork(artworkUrl) {
  if (!currentSongData) return;
              
              // Update the saved state with the new artwork URL
              saveState({
                state: 'results',
                songData: {
                  title: currentSongData.title,
                  artist: currentSongData.artist,
                  lyrics: originalLyrics,
                  youtubeId: currentSongData.youtubeId || '',
                  spotifyId: currentSongData.spotifyId || '',
      albumArtworkSrc: artworkUrl
    }
  });
}

/**
 * Reset enhancement UI elements
 */
function resetEnhancementUI() {
  // Reset translate dropdown
  document.querySelectorAll('.translate-option').forEach(option => {
    option.classList.remove('active');
  });
  document.querySelector('.translate-option[data-lang="original"]').classList.add('active');
  
  // Reset recommendations tab
  document.getElementById('recommendations-placeholder').classList.remove('hidden');
  document.getElementById('recommendations-loading').classList.add('hidden');
  document.getElementById('recommendations-list').innerHTML = `
    <div id="recommendations-placeholder">
      <p>Find more songs like this one.</p>
      <button id="get-recommendations" class="btn btn-sm btn-outline-primary">Get Recommendations</button>
    </div>
  `;
  
  // Add event listeners to new buttons
  document.getElementById('get-recommendations').addEventListener('click', handleGetRecommendations);
}

/**
 * Handle translation option click
 */
async function handleTranslateOption(event) {
  event.preventDefault();
  
  const langOption = event.target;
  const targetLang = langOption.dataset.lang;
  
  // Skip if already on this language
  if (langOption.classList.contains('active')) {
    return;
  }
  
  // Update active state
  document.querySelectorAll('.translate-option').forEach(option => {
    option.classList.remove('active');
  });
  langOption.classList.add('active');
  
  // If original, just restore original lyrics
  if (targetLang === 'original') {
    lyricsElem.textContent = originalLyrics;
    return;
  }
  
  // Show loading state
  lyricsElem.classList.add('hidden');
  lyricsLoadingElem.classList.remove('hidden');
  
  try {
    // Call the translation API
    const response = await fetch(`${API_BASE_URL}/translate_lyrics`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        lyrics: originalLyrics,
        target_lang: targetLang
      })
    });
    
    const data = await response.json();
    
    if (data.status === 'success') {
      // Use the shared formatting function for translated lyrics
      lyricsElem.textContent = formatLyrics(data.translated_lyrics);
    } else {
      lyricsElem.textContent = `Translation failed: ${data.message || 'Unknown error'}`;
    }
  } catch (error) {
    console.error('Translation error:', error);
    lyricsElem.textContent = `Translation error: ${error.message}`;
  } finally {
    // Hide loading state
    lyricsElem.classList.remove('hidden');
    lyricsLoadingElem.classList.add('hidden');
  }
}

/**
 * Handle get recommendations button click
 */
async function handleGetRecommendations() {
  if (!currentSongData) return;
  
  // Get elements
  const placeholderElem = document.getElementById('recommendations-placeholder');
  const recommendationsListElem = document.getElementById('recommendations-list');
  
  // Show loading state
  placeholderElem.classList.add('hidden');
  recommendationsLoadingElem.classList.remove('hidden');
  
  try {
    // Call the recommendations API
    const response = await fetch(`${API_BASE_URL}/similar_songs`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        title: currentSongData.title,
        artist: currentSongData.artist,
        lyrics: originalLyrics
      })
    });
    
    const data = await response.json();
    
    if (data.status === 'success') {
      // Build recommendations HTML
      const recommendations = data.recommendations;
      let html = '';
      
      recommendations.forEach(rec => {
        html += `
          <div class="recommendation-item">
            <div class="recommendation-title">${rec.title}</div>
            <div class="recommendation-artist">${rec.artist} (${rec.year})</div>
            <div class="recommendation-reason">${rec.reason}</div>
          </div>
        `;
      });
      
      // Update the recommendations list
      recommendationsListElem.innerHTML = html;
      
      // Save the recommendations to storage
      const currentState = await getStoredState();
      if (currentState && currentState.songData) {
        currentState.songData.recommendations = html;
        saveState(currentState);
      }
    } else {
      recommendationsListElem.innerHTML = `<p class="text-danger">Recommendations failed: ${data.message || 'Unknown error'}</p>`;
    }
  } catch (error) {
    console.error('Recommendations error:', error);
    recommendationsListElem.innerHTML = `<p class="text-danger">Recommendations error: ${error.message}</p>`;
  } finally {
    // Hide loading state
    recommendationsLoadingElem.classList.add('hidden');
  }
}

/**
 * Get the current stored state as a Promise
 */
function getStoredState() {
  return new Promise((resolve) => {
    chrome.storage.local.get(['lyrikaState'], function(result) {
      resolve(result.lyrikaState);
    });
  });
}

/**
 * Convert markdown to HTML (simple version)
 */
function convertMarkdownToHTML(markdown) {
  if (!markdown) return '';
  
  // Handle headers
  markdown = markdown.replace(/^# (.*?)$/gm, '<h3>$1</h3>');
  markdown = markdown.replace(/^## (.*?)$/gm, '<h4>$1</h4>');
  markdown = markdown.replace(/^### (.*?)$/gm, '<h5>$1</h5>');
  
  // Handle paragraphs
  const paragraphs = markdown.split('\n\n');
  return paragraphs.map(p => {
    if (p.startsWith('<h')) {
      return p;
    }
    return `<p>${p}</p>`;
  }).join('');
}

/**
 * Display error message
 */
function displayError(message) {
  errorMessageElem.textContent = message || "Couldn't identify the song. Please try again.";
  showState(errorState);
  
  // Save error state
  saveState({
    state: 'error',
    errorMessage: message
  });
}

/**
 * Reset to initial state
 */
function resetToInitialState() {
  showState(initialState);
  
  // Clear previous data
  songTitleElem.textContent = '';
  artistElem.textContent = '';
  lyricsElem.textContent = '';
  youtubeLink.classList.add('hidden');
  spotifyLink.classList.add('hidden');
  appleMusicLink.classList.add('hidden');
  albumArtworkElem.src = 'assets/icons/icon128.png';
  
  // Clear any copied state
  songTitleElem.dataset.copied = false;
  
  // Clear current song data
  currentSongData = null;
  originalLyrics = '';
  
  // Clear saved state
  chrome.storage.local.remove('lyrikaState', function() {
    console.log('State cleared');
  });
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
  
  // Show loading state in search tab
  document.getElementById('search-loading').classList.remove('hidden');
  
  chrome.runtime.sendMessage({
    action: 'manualSearch',
    songTitle: songTitle,
    artist: artist
  }, response => {
    console.log('Manual search response:', response);
    
    // Hide loading state
    document.getElementById('search-loading').classList.add('hidden');
    
    if (response && response.status === 'success') {
      // Apply the same formatting to manual search results
      if (response.lyrics) {
        response.lyrics = formatLyrics(response.lyrics);
      }
      displayResults(response);
      
      // Switch to lyrics tab to show results
      document.getElementById('lyrics-tab').click();
    } else {
      displayError(response?.message || 'Failed to find lyrics for this song.');
    }
  });
}

/**
 * Handle YouTube link click
 */
function openYoutubeLink(event) {
  // Prevent default link behavior
  event.preventDefault();
  
  // Open link in new tab
  chrome.tabs.create({ url: youtubeLink.href });
}

/**
 * Handle Spotify link click
 */
function openSpotifyLink(event) {
  // Prevent default link behavior
  event.preventDefault();
  
  // Open link in new tab
  chrome.tabs.create({ url: spotifyLink.href });
}

/**
 * Handle Apple Music link click
 */
function openAppleMusicLink(event) {
  // Prevent default link behavior
  event.preventDefault();
  
  // Open link in new tab
  chrome.tabs.create({ url: appleMusicLink.href });
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