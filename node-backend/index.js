const express = require('express');
const bodyParser = require('body-parser');
const axios = require('axios');

const app = express();
app.use(bodyParser.urlencoded({ extended: false }));

const TWILIO_AUTH_TOKEN = process.env.TWILIO_AUTH_TOKEN || 'your_twilio_auth_token';
const TWILIO_ACCOUNT_SID = process.env.TWILIO_ACCOUNT_SID || 'your_twilio_account_sid';
const GEMINI_API_KEY = 'AIzaSyB9hywgcDdic5lcAQQu9vRvwe3ddz0L08M';

// Gemini API endpoint (replace with actual endpoint)
const GEMINI_API_URL = 'https://api.gemini.com/v1/chat';

app.post('/twilio-webhook', async (req, res) => {
    const incomingMsg = req.body.Body;
    const sender = req.body.From;

    try {
        const geminiRes = await axios.post(GEMINI_API_URL, {
            message: incomingMsg
        }, {
            headers: { Authorization: `Bearer ${GEMINI_API_KEY}` }
        });
        const aiReply = geminiRes.data.reply || 'Sorry, I could not process your request.';
        res.type('xml').send(`<Response><Message>${aiReply}</Message></Response>`);
    } catch (err) {
        res.type('xml').send('<Response><Message>Error contacting Gemini API.</Message></Response>');
    }
});

app.listen(5000, () => {
    console.log('Node.js server running on port 5000');
});
