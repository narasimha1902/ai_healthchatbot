# Health Chatbot with Twilio & Gemini API

This project provides two backend implementations (Python/Flask and Node.js/Express) for a health chatbot using Twilio for messaging and Gemini API for AI responses.

## Setup Instructions

### Python Backend
1. Go to `python-backend` folder.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set environment variables for Twilio and Gemini API keys.
4. Run the server:
   ```bash
   python app.py
   ```

### Node.js Backend
1. Go to `node-backend` folder.
2. Install dependencies:
   ```bash
   npm install
   ```
3. Set environment variables for Twilio and Gemini API keys.
4. Run the server:
   ```bash
   node index.js
   ```

## Twilio Webhook
Configure your Twilio account to send incoming messages to `/twilio-webhook` endpoint of the running backend.

## Gemini API
Replace the placeholder Gemini API key and endpoint with your actual credentials.

---

Feel free to provide your Gemini API key to enable full functionality.
