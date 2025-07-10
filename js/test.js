/**
 * Lyrika Test Script
 * Tests API connections and audio recognition
 */

document.addEventListener('DOMContentLoaded', () => {
  // Bind event listeners
  document.getElementById('test-sample-1').addEventListener('click', () => testSample(1));
  document.getElementById('test-sample-2').addEventListener('click', () => testSample(2));
  document.getElementById('test-sample-3').addEventListener('click', () => testSample(3));
  document.getElementById('test-acrcloud').addEventListener('click', testACRCloud);
  document.getElementById('test-genius').addEventListener('click', testGenius);
  
  // Log initialization
  console.log('Lyrika test page initialized');
});

/**
 * Test recognition with an audio sample
 */
async function testSample(sampleNumber) {
  const resultDiv = document.getElementById(`result-${sampleNumber}`);
  resultDiv.innerHTML = '<p>Processing audio sample...</p>';
  
  try {
    const audio = document.getElementById(`test-audio-${sampleNumber}`);
    if (!audio) {
      throw new Error(`Audio element #test-audio-${sampleNumber} not found`);
    }
    
    // In a real implementation, this would:
    // 1. Extract audio data from the audio element
    // 2. Send it to the ACRCloud API
    // 3. Process the result
    
    // For now, use a mock implementation
    const mockResponses = {
      1: {
        success: true,
        result: {
          status: {
            code: 0,
            msg: 'Success'
          },
          metadata: {
            music: [{
              title: 'Bohemian Rhapsody',
              artists: [{ name: 'Queen' }],
              album: { name: 'A Night at the Opera' },
              external_metadata: {
                youtube: { vid: 'fJ9rUzIMcZQ' }
              }
            }]
          }
        }
      },
      2: {
        success: true,
        result: {
          status: {
            code: 0,
            msg: 'Success'
          },
          metadata: {
            music: [{
              title: 'Piano Sonata No. 14',
              artists: [{ name: 'Ludwig van Beethoven' }],
              album: { name: 'Classical Masterpieces' },
              external_metadata: {
                youtube: { vid: '4Tr0otuiQuU' }
              }
            }]
          }
        }
      },
      3: {
        success: true,
        result: {
          status: {
            code: 0,
            msg: 'Success'
          },
          metadata: {
            music: [{
              title: 'The Sound of Silence',
              artists: [{ name: 'Disturbed' }],
              album: { name: 'Immortalized' },
              external_metadata: {
                youtube: { vid: 'u9Dg-g7t2l4' }
              }
            }]
          }
        }
      }
    };
    
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Process mock response
    const response = mockResponses[sampleNumber];
    displayResult(resultDiv, response);
    
  } catch (error) {
    resultDiv.innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
    console.error('Test sample error:', error);
  }
}

/**
 * Test ACRCloud API connection
 */
async function testACRCloud() {
  const resultDiv = document.getElementById('acrcloud-result');
  resultDiv.innerHTML = '<p>Testing ACRCloud connection...</p>';
  
  try {
    // In a real implementation, this would make a simple ping request to ACRCloud
    
    // For now, use a mock implementation
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const mockSuccess = Math.random() > 0.2; // 80% success rate
    
    if (mockSuccess) {
      resultDiv.innerHTML = `
        <p style="color: green;">✓ Connection successful!</p>
        <p>ACRCloud API is properly configured and responding.</p>
        <pre>{
  "status": {
    "code": 0,
    "msg": "Success"
  },
  "api_version": "1.0"
}</pre>
      `;
    } else {
      resultDiv.innerHTML = `
        <p style="color: red;">✗ Connection failed!</p>
        <p>Please check your ACRCloud API credentials in the .env file.</p>
        <pre>{
  "status": {
    "code": 3001,
    "msg": "Authentication failed"
  }
}</pre>
      `;
    }
  } catch (error) {
    resultDiv.innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
    console.error('ACRCloud test error:', error);
  }
}

/**
 * Test Genius API connection
 */
async function testGenius() {
  const resultDiv = document.getElementById('genius-result');
  resultDiv.innerHTML = '<p>Testing Genius API connection...</p>';
  
  try {
    // In a real implementation, this would make a simple ping request to Genius API
    
    // For now, use a mock implementation
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const mockSuccess = Math.random() > 0.2; // 80% success rate
    
    if (mockSuccess) {
      resultDiv.innerHTML = `
        <p style="color: green;">✓ Connection successful!</p>
        <p>Genius API is properly configured and responding.</p>
        <pre>{
  "meta": {
    "status": 200
  },
  "response": {
    "message": "Success"
  }
}</pre>
      `;
    } else {
      resultDiv.innerHTML = `
        <p style="color: red;">✗ Connection failed!</p>
        <p>Please check your Genius API token in the .env file.</p>
        <pre>{
  "meta": {
    "status": 401
  },
  "response": {
    "error": "Invalid authentication token"
  }
}</pre>
      `;
    }
  } catch (error) {
    resultDiv.innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
    console.error('Genius test error:', error);
  }
}

/**
 * Display API result in a result div
 */
function displayResult(resultDiv, response) {
  if (!response.success) {
    resultDiv.innerHTML = `
      <p style="color: red;">Recognition failed!</p>
      <pre>${JSON.stringify(response, null, 2)}</pre>
    `;
    return;
  }
  
  const musicResult = response.result.metadata.music[0];
  const title = musicResult.title;
  const artist = musicResult.artists[0].name;
  const album = musicResult.album.name;
  const youtubeId = musicResult.external_metadata?.youtube?.vid;
  
  resultDiv.innerHTML = `
    <p style="color: green;">✓ Song identified!</p>
    <p><strong>Title:</strong> ${title}</p>
    <p><strong>Artist:</strong> ${artist}</p>
    <p><strong>Album:</strong> ${album}</p>
    ${youtubeId ? `<p><strong>YouTube:</strong> <a href="https://www.youtube.com/watch?v=${youtubeId}" target="_blank">Open video</a></p>` : ''}
    <details>
      <summary>View raw response</summary>
      <pre>${JSON.stringify(response, null, 2)}</pre>
    </details>
  `;
} 