import os
from flask import Flask, request
import requests

app = Flask(__name__)

TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', 'your_twilio_auth_token')
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', 'your_twilio_account_sid')
GEMINI_API_KEY = 'AIzaSyB9hywgcDdic5lcAQQu9vRvwe3ddz0L08M'

# Gemini API endpoint (replace with actual endpoint)
GEMINI_API_URL = 'https://api.gemini.com/v1/chat'

@app.route('/twilio-webhook', methods=['POST'])
@app.route('/whatsapp/twilio', methods=['POST'])
def twilio_webhook():
    incoming_msg = request.form.get('Body')
    sender = request.form.get('From')

    # Call Gemini API
    gemini_response = requests.post(
        GEMINI_API_URL,
        headers={'Authorization': f'Bearer {GEMINI_API_KEY}'},
        json={'message': incoming_msg}
    )
    ai_reply = gemini_response.json().get('reply', 'Sorry, I could not process your request.')

    # Respond to Twilio (SMS/WhatsApp)
    response = f"<Response><Message>{ai_reply}</Message></Response>"
    return response, 200, {'Content-Type': 'application/xml'}

if __name__ == '__main__':
    app.run(port=8000)
