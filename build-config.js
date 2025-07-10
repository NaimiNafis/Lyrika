/**
 * Lyrika Build Configuration Script
 * Injects API keys from .env file into the configuration
 */

const fs = require('fs');
const path = require('path');
const dotenv = require('dotenv');

// Load environment variables
dotenv.config();

console.log('Building Lyrika configuration...');

// Ensure required env variables are present
const requiredEnvVars = [
  'ACRCLOUD_HOST',
  'ACRCLOUD_ACCESS_KEY',
  'ACRCLOUD_ACCESS_SECRET',
  'GENIUS_ACCESS_TOKEN'
];

const missingVars = requiredEnvVars.filter(varName => !process.env[varName]);

if (missingVars.length > 0) {
  console.error('Error: Missing required environment variables:');
  missingVars.forEach(varName => console.error(`  - ${varName}`));
  console.error('Please create a .env file based on sample.env with your API keys.');
  process.exit(1);
}

// ACRCloud config template
const acrcloudTemplate = `/**
 * ACRCloud API Client Configuration
 * GENERATED FILE - DO NOT EDIT DIRECTLY
 */

// Configuration
export const config = {
  host: "__ACRCLOUD_HOST__",
  access_key: "__ACRCLOUD_ACCESS_KEY__",
  access_secret: "__ACRCLOUD_ACCESS_SECRET__",
  timeout: 10 // seconds
};
`;

// Replace placeholders with actual values
let acrcloudContent = acrcloudTemplate
  .replace('__ACRCLOUD_HOST__', process.env.ACRCLOUD_HOST)
  .replace('__ACRCLOUD_ACCESS_KEY__', process.env.ACRCLOUD_ACCESS_KEY)
  .replace('__ACRCLOUD_ACCESS_SECRET__', process.env.ACRCLOUD_ACCESS_SECRET);

// Write to ACRCloud config file
const acrcloudConfigPath = path.join(__dirname, 'js', 'api', 'acrcloud-config.js');
fs.writeFileSync(acrcloudConfigPath, acrcloudContent);
console.log('ACRCloud config file created with secure keys');

// Genius config template
const geniusTemplate = `/**
 * Genius API Client Configuration
 * GENERATED FILE - DO NOT EDIT DIRECTLY
 */

// Configuration
export const config = {
  access_token: "__GENIUS_ACCESS_TOKEN__"
};
`;

// Replace placeholders with actual values
let geniusContent = geniusTemplate
  .replace('__GENIUS_ACCESS_TOKEN__', process.env.GENIUS_ACCESS_TOKEN);

// Write to Genius config file
const geniusConfigPath = path.join(__dirname, 'js', 'api', 'genius-config.js');
fs.writeFileSync(geniusConfigPath, geniusContent);
console.log('Genius config file created with secure keys');

console.log('Configuration build complete!'); 