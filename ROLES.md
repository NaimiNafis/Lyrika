# Team Roles & Responsibilities

This document outlines the specific responsibilities, tasks, and deliverables for each team member working on the Lyrika browser extension hackathon project.

## API & Core Logic Lead (Phong)

### Primary Responsibilities
- Implement audio capture functionality
- Build API integration with ACRCloud and Genius
- Create data processing pipeline
- Implement edge case handling

### Key Implementation Details

#### Audio Capture & Recognition
- Use `chrome.tabCapture` API to get the audio stream from the active tab
- Process the audio data into a format compatible with ACRCloud API
- Implement recording duration control (ideally 10-15 seconds of audio)
- Add proper error handling for permission issues

#### ACRCloud Integration
- Build the ACRCloud client with the following structure:
  ```javascript
  // Sample ACRCloud client implementation
  class ACRCloudClient {
    constructor(config) {
      this.host = config.host;
      this.accessKey = config.access_key;
      this.accessSecret = config.access_secret;
    }
    
    async identifySong(audioData) {
      // Prepare the audio data and make the API request
      // Return standardized response
    }
  }
  ```
- Handle ACRCloud response format and extract relevant metadata
- Extract YouTube ID from `external_metadata.youtube.vid` when available

#### Genius Lyrics API
- Create a Genius API client to fetch lyrics based on song title and artist
- Implement fallback search for cover songs (first search with cover artist, then with just song title)
- Handle special cases like instrumental tracks (when lyrics are empty/null)

#### Data Transformation
- Format API responses according to the agreed data contract:
  ```javascript
  // For a successful match
  {
    status: 'success',
    title: 'Bohemian Rhapsody',
    artist: 'Queen',
    lyrics: 'Is this the real life? Is this just fantasy?...',
    youtubeId: 'fJ9rUzIMcZQ'
  }

  // For an error or no match
  {
    status: 'error',
    message: 'Could not identify song.'
  }
  ```

### Detailed Tasks

#### Setup Phase
- [ ] Set up `background.js` initial structure
- [ ] Configure Chrome's `tabCapture` API in manifest.json
- [ ] Create API client modules structure
- [ ] **Security**: Create the `.env` file structure and add to `.gitignore`
- [ ] **Security**: Set up the build script for API key injection (`build-config.js`)
- [ ] Create `sample.env` file with empty values for the team

#### Development Phase
- [ ] Implement audio stream capture from active tab
- [ ] Create audio data processing for ACRCloud format
- [ ] Implement `acrcloud-client.js` with identification logic
- [ ] Implement `genius-client.js` for lyrics fetching
- [ ] Create logic to handle instrumental tracks (no lyrics)
- [ ] Create logic to handle cover songs (artist mismatch)
- [ ] Implement data transformation to the agreed "contract" format

#### Testing Phase
- [ ] Create test cases for each API connection
- [ ] Test audio capture in various scenarios
- [ ] Test identification with different song types
- [ ] Document any API limitations discovered

### API Security Responsibilities
- Implement the environment variables approach (`.env` with build script)
- Document API key acquisition process for other team members
- Create secure storage and retrieval for API credentials
- Test API connections with proper authentication

### Dependencies
- Requires UI contract from Frontend Lead before finalizing data output structure
- Coordinate with Integration Lead on message passing between background and popup scripts

---

## Frontend & UI Lead (Alvin)

### Primary Responsibilities
- Design the extension popup interface
- Create all CSS styling
- Build UI state components (loading, results, error)
- Ensure responsive and accessible design

### Key Implementation Details

#### User Interface Components
- Design the popup with three main states:
  1. **Initial State**: Button to start listening
  2. **Listening State**: Animation indicating audio capture in progress
  3. **Results State**: Display song title, artist, lyrics, and action buttons

#### UI Elements
- Implement components for:
  - Song title and artist display (also serves as copy-to-clipboard trigger)
  - Lyrics container with proper scrolling for long texts
  - YouTube icon for direct song access
  - Status indicators for different states
  - Error messages with clear instructions

#### Manual Fallback Input
- Create a hidden form that appears after failed recognition:
  ```html
  <div id="manual-input" class="hidden">
    <p>Couldn't identify the song? Enter details manually:</p>
    <input type="text" id="manual-song" placeholder="Song Title">
    <input type="text" id="manual-artist" placeholder="Artist">
    <button id="manual-search">Search Lyrics</button>
  </div>
  ```

#### Special Cases UI
- Design UI variants for:
  - Instrumental tracks (show message: "Song Identified! This is an instrumental track.")
  - Cover songs (show note: "Displaying original version lyrics.")
  - Failed recognition (clear error message with manual option)

### Detailed Tasks

#### Setup Phase
- [ ] Create `popup.html` base structure
- [ ] Set up `popup.css` with design system (colors, typography, spacing)
- [ ] Design icon assets for extension (16px, 48px, 128px)
- [ ] Finalize the UI/UX flow with all states
- [ ] **Security**: Add proper input validation for any user inputs

#### Development Phase
- [ ] Build loading/listening state UI
- [ ] Build results display with song info and lyrics
- [ ] Create error states with helpful messages
- [ ] Implement instrumental track display variant
- [ ] Create UI for manual input fallback
- [ ] Ensure all UI is accessible and responsive

#### Testing Phase
- [ ] Test UI across all possible states
- [ ] Validate proper display of various result types
- [ ] Ensure error states are user-friendly
- [ ] Check for any UI edge cases or overflow issues

### API Security Responsibilities
- If implementing the user input API key option, create secure input fields
- Ensure any displayed data is properly sanitized
- Make sure error messages don't expose sensitive information

### Dependencies
- Needs data contract from API Lead to build appropriate display components
- Coordinate with Integration Lead on UI interaction events

---

## Features & Integration Lead (Naimi)

### Primary Responsibilities
- Connect backend logic with frontend display
- Implement user interaction features
- Manage Git workflow and PR reviews
- Package extension for distribution

### Key Implementation Details

#### Message Passing Implementation
- Create a communication channel between background.js and popup.js:
  ```javascript
  // In popup.js
  chrome.runtime.sendMessage({action: "startListening"}, function(response) {
    // Handle the response
  });
  
  // In background.js
  chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.action === "startListening") {
      // Start the audio capture and recognition
      startRecognition().then(result => {
        sendResponse(result);
      });
      return true; // Will respond asynchronously
    }
  });
  ```

#### Performance Optimization
- Implement debounce functionality to prevent multiple API calls:
  ```javascript
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
  
  // Usage
  document.getElementById('start-listening').addEventListener('click', 
    debounce(startListening, 300));
  ```

#### Copy to Clipboard Feature
- Implement click event on song title to copy to clipboard:
  ```javascript
  document.getElementById('song-title').addEventListener('click', function() {
    const songInfo = `${songTitle} by ${artist}`;
    navigator.clipboard.writeText(songInfo)
      .then(() => {
        // Show "Copied!" feedback
        this.dataset.copied = true;
        setTimeout(() => {
          this.dataset.copied = false;
        }, 2000);
      });
  });
  ```

#### YouTube Link Feature
- Create YouTube link from song ID:
  ```javascript
  function createYouTubeLink(videoId) {
    const link = document.getElementById('youtube-link');
    if (videoId) {
      link.href = `https://www.youtube.com/watch?v=${videoId}`;
      link.classList.remove('hidden');
    } else {
      link.classList.add('hidden');
    }
  }
  ```

#### Build & Package Script
- Implement `package.sh` script for extension packaging:
  ```bash
  #!/bin/bash
  
  # Ensure we're in the project root
  cd "$(dirname "$0")"
  
  # Create build directory
  mkdir -p build
  
  # Copy necessary files
  cp -r manifest.json popup.html assets css js build/
  
  # Remove development/test files
  rm -rf build/js/test.js
  rm -rf build/assets/test-audio
  
  # Replace API keys with production values if specified
  if [ -f "prod-config.js" ]; then
    cp prod-config.js build/js/api/config.js
  fi
  
  # Create zip file for Chrome Web Store
  cd build
  zip -r ../lyrika-extension.zip *
  
  echo "Extension packaged to lyrika-extension.zip"
  ```

#### Demo Preparation
- Create demo assets with test songs and expected results
- Prepare a test suite for different scenarios (instrumentals, covers, errors)
- Document test cases in a structured format

### Detailed Tasks

#### Setup Phase
- [ ] Create and manage GitHub repository
- [ ] Set up branch protection rules
- [ ] Create PR templates and review process
- [ ] **Security**: Add security scanning in GitHub workflow
- [ ] **Security**: Implement the package.sh script with security considerations
- [ ] Create initial npm project with appropriate dependencies

#### Development Phase
- [ ] Implement message passing between background.js and popup.js
- [ ] Create copy-to-clipboard functionality
- [ ] Build YouTube link feature
- [ ] Implement debounce functionality for button clicks
- [ ] Add processing state tracking
- [ ] Create manual fallback mechanism timer
- [ ] Implement Chrome storage for user settings/history

#### Testing Phase
- [ ] Test full extension integration
- [ ] Create demo script and assets
- [ ] Prepare test cases for edge conditions
- [ ] Document known issues or limitations
- [ ] Create extension package for submission

### API Security Responsibilities
- Manage API keys for the team in a secure way
- Review code for any security vulnerabilities
- Implement secure storage for any user data
- Create the package script that handles API keys securely

### Dependencies
- Needs API implementation from API Lead to connect to frontend
- Requires UI components from Frontend Lead to attach functionality

---

## Cross-Team Security Responsibilities

### Repository & Code Security
- All members should ensure not to commit API keys or credentials
- Use environment variables for sensitive data
- Review each other's code for security issues
- Follow secure coding practices

### API Key Security Implementation
- Use the environment variables with build process approach:
  1. Create a `.env` file excluded from Git:
  ```
  # .env (add to .gitignore)
  ACRCLOUD_HOST=your_host
  ACRCLOUD_ACCESS_KEY=your_access_key
  ACRCLOUD_ACCESS_SECRET=your_access_secret
  GENIUS_ACCESS_TOKEN=your_token
  ```
  
  2. Create a build script that replaces placeholders with actual values:
  ```javascript
  // build-config.js
  const fs = require('fs');
  const dotenv = require('dotenv');
  
  // Load environment variables
  dotenv.config();
  
  // Template with placeholders
  const configTemplate = `
  const CONFIG = {
    ACRCLOUD: {
      host: "__ACRCLOUD_HOST__",
      access_key: "__ACRCLOUD_ACCESS_KEY__",
      access_secret: "__ACRCLOUD_ACCESS_SECRET__",
    },
    GENIUS: {
      access_token: "__GENIUS_ACCESS_TOKEN__"
    }
  };
  `;
  
  // Replace placeholders with actual values
  let configContent = configTemplate
    .replace('__ACRCLOUD_HOST__', process.env.ACRCLOUD_HOST)
    .replace('__ACRCLOUD_ACCESS_KEY__', process.env.ACRCLOUD_ACCESS_KEY)
    .replace('__ACRCLOUD_ACCESS_SECRET__', process.env.ACRCLOUD_ACCESS_SECRET)
    .replace('__GENIUS_ACCESS_TOKEN__', process.env.GENIUS_ACCESS_TOKEN);
  
  // Write to config file
  fs.writeFileSync('./js/api/config.js', configContent);
  console.log('Config file created with secure keys');
  ```

### API Key Management
1. Each team member should:
   - Create their own ACRCloud and Genius API accounts
   - Generate their own API keys for development
   - Create their personal `.env` file (not committed to Git)
   - Use the provided `sample.env` file as a template

2. For the final demo:
   - The Integration Lead will collect a single set of API keys for the demo
   - Keys will be securely injected during the build process
   - No API keys should be visible in the final presentation

### Extension Permissions
- Only request necessary permissions in manifest.json
- Document why each permission is needed
- Be transparent about audio capture functionality

---

## Timeline Integration

### Day 1 Morning
- **API Lead**: Set up API clients and test connections
- **Frontend Lead**: Create basic UI components and states
- **Integration Lead**: Set up repository and security practices

### Day 1 Afternoon
- **API Lead**: Implement audio capture and song identification
- **Frontend Lead**: Complete all UI states and styling
- **Integration Lead**: Begin connecting components

### Day 2 Morning
- **API Lead**: Complete edge case handling and data processing
- **Frontend Lead**: Finalize UI and address any design issues
- **Integration Lead**: Implement all interactive features

### Day 2 Afternoon
- All members collaborate on integration
- Test full application flow
- Prepare demonstration
- Package extension for submission

---

## Communication Protocol

- Use GitHub issues for task tracking
- Use pull requests for code review
- Daily sync meeting (morning and evening)
- Slack/Discord for quick communication
- Document all API contracts and interfaces

## Definition of Done

A task is considered complete when:
1. Code is written and tested
2. Code has been reviewed by at least one other team member
3. No security vulnerabilities are present
4. Code is merged to the main branch
5. Documentation is updated if needed
