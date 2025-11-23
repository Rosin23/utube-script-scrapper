/**
 * JavaScript/Node.js Examples for YouTube Script Scraper API
 *
 * This file demonstrates API usage with JavaScript's fetch API.
 * Works in both browser and Node.js (with node-fetch).
 */

const BASE_URL = 'http://localhost:8000';

/**
 * Get video metadata and transcript
 * @param {string} videoUrl - YouTube video URL
 * @param {string[]} languages - Preferred subtitle languages
 * @returns {Promise<Object>} Video information
 */
async function getVideoInfo(videoUrl, languages = ['ko', 'en']) {
  const response = await fetch(`${BASE_URL}/video/info`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      video_url: videoUrl,
      languages: languages,
      prefer_manual: true,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }

  return response.json();
}

/**
 * Scrape video with AI enhancements
 * @param {string} videoUrl - YouTube video URL
 * @param {Object} options - AI options
 * @returns {Promise<Object>} Enhanced video data
 */
async function scrapeVideoWithAI(videoUrl, options = {}) {
  const {
    enableSummary = true,
    enableTranslation = false,
    targetLanguage = 'en',
    enableTopics = true,
    numTopics = 5,
  } = options;

  const response = await fetch(`${BASE_URL}/video/scrape`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      video_url: videoUrl,
      enable_summary: enableSummary,
      summary_max_points: 5,
      enable_translation: enableTranslation,
      target_language: targetLanguage,
      enable_topics: enableTopics,
      num_topics: numTopics,
      output_format: 'json',
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }

  return response.json();
}

/**
 * Get playlist information
 * @param {string} playlistUrl - YouTube playlist URL
 * @param {number} maxVideos - Maximum videos to retrieve
 * @returns {Promise<Object>} Playlist information
 */
async function getPlaylistInfo(playlistUrl, maxVideos = null) {
  const body = { playlist_url: playlistUrl };
  if (maxVideos !== null) {
    body.max_videos = maxVideos;
  }

  const response = await fetch(`${BASE_URL}/playlist/info`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }

  return response.json();
}

/**
 * Generate AI summary
 * @param {string} text - Text to summarize
 * @param {number} maxPoints - Maximum summary points
 * @param {string} language - Summary language
 * @returns {Promise<string>} Summary text
 */
async function generateSummary(text, maxPoints = 5, language = 'ko') {
  const response = await fetch(`${BASE_URL}/ai/summary`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      text,
      max_points: maxPoints,
      language,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }

  const data = await response.json();
  return data.summary;
}

/**
 * Translate text
 * @param {string} text - Text to translate
 * @param {string} targetLanguage - Target language code
 * @param {string} sourceLanguage - Source language code (optional)
 * @returns {Promise<string>} Translated text
 */
async function translateText(text, targetLanguage, sourceLanguage = null) {
  const body = {
    text,
    target_language: targetLanguage,
  };
  if (sourceLanguage) {
    body.source_language = sourceLanguage;
  }

  const response = await fetch(`${BASE_URL}/ai/translate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }

  const data = await response.json();
  return data.translated_text;
}

/**
 * Extract topics from text
 * @param {string} text - Text to analyze
 * @param {number} numTopics - Number of topics to extract
 * @param {string} language - Topic language
 * @returns {Promise<string[]>} List of topics
 */
async function extractTopics(text, numTopics = 5, language = 'en') {
  const response = await fetch(`${BASE_URL}/ai/topics`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      text,
      num_topics: numTopics,
      language,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }

  const data = await response.json();
  return data.topics;
}

// Example Usage (for Node.js)
async function main() {
  try {
    // Example 1: Get video information
    console.log('Example 1: Getting video information...');
    const videoData = await getVideoInfo('https://www.youtube.com/watch?v=dQw4w9WgXcQ');
    console.log(`Title: ${videoData.metadata.title}`);
    console.log(`Channel: ${videoData.metadata.channel}`);
    console.log(`Transcript entries: ${videoData.transcript.length}`);

    // Example 2: Scrape with AI
    console.log('\nExample 2: Scraping with AI...');
    const aiData = await scrapeVideoWithAI('https://www.youtube.com/watch?v=jNQXAC9IVRw', {
      enableSummary: true,
      enableTopics: true,
    });
    console.log(`Summary: ${aiData.summary.substring(0, 100)}...`);
    console.log(`Topics: ${aiData.key_topics}`);

    // Example 3: Get playlist info
    console.log('\nExample 3: Getting playlist information...');
    const playlistData = await getPlaylistInfo(
      'https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf',
      5
    );
    console.log(`Playlist: ${playlistData.playlist_info.title}`);
    console.log(`Total videos: ${playlistData.total_videos}`);

    // Example 4: Generate summary
    console.log('\nExample 4: Generating summary...');
    const summary = await generateSummary('Your long text here...', 3);
    console.log(`Summary: ${summary}`);

    // Example 5: Translate text
    console.log('\nExample 5: Translating text...');
    const translation = await translateText('안녕하세요', 'en');
    console.log(`Translation: ${translation}`);

    // Example 6: Extract topics
    console.log('\nExample 6: Extracting topics...');
    const topics = await extractTopics('Sample text about machine learning...', 3);
    console.log(`Topics: ${topics}`);
  } catch (error) {
    console.error(`Error: ${error.message}`);
  }
}

// Run examples if called directly
if (typeof require !== 'undefined' && require.main === module) {
  main();
}

// Export functions for use as module
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    getVideoInfo,
    scrapeVideoWithAI,
    getPlaylistInfo,
    generateSummary,
    translateText,
    extractTopics,
  };
}
