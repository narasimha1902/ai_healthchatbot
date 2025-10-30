# services/twilio.py
from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()

account_sid = os.getenv("account_sid")
auth_token = os.getenv("auth_token")
from_number = os.getenv("FROM")  # should be 'whatsapp:+14155238886'

client = Client(account_sid, auth_token)

def send_message(to: str, message: str) -> None:
    """
    Sends WhatsApp message using Twilio.
    Automatically handles 'whatsapp:' prefix to prevent 21211 error.
    """
    if not to.startswith("whatsapp:"):
        to_number = f"whatsapp:{to}"
    else:
        to_number = to

    client.messages.create(
        from_=from_number,
        body=message,
        to=to_number
    )
