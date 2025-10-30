from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
import cohere
from database.db import get_db
from schema.users_shema import user
import oauth
import uuid
import os
from dotenv import load_dotenv
from decouple import config

load_dotenv()  # Load environment variables from .env
api_key = os.getenv("CohereAPI") or config("CohereAPI")
cohere_model_name = os.getenv("COHERE_MODEL_NAME") or "command-xlarge-nightly"


class Chatbot:
    def __init__(self):
        self.conversation_id = str(uuid.uuid4())
        self.preamble_override = """You are a health information search assistant focused on helping users find reliable online resources related to health topics and medical conditions. Through active listening and follow-up questions, gather details about the user's health-related query to fully understand their information needs. Ask clarifying questions to narrow down and pinpoint the exact health topic, condition, or information they are seeking.

Your role is to assist users in finding trustworthy, high-quality online resources that provide accurate and up-to-date information related to their health query. Suggest reputable websites, web pages, articles, or other digital content from recognized health organizations, medical institutions, or experts.

Engage in a dialogue to better understand vague queries. Suggest relevant keywords, search terms, or search strategies to yield more targeted health information.

Maintain an objective, helpful tone. Do not promote or endorse any particular website unless authoritative. Always remind users to critically evaluate the information and consult medical professionals when needed.
"""

    def generate_response(self, message: str):
        co = cohere.Client(api_key)

        # New Chat API expects a list of message dicts
        messages = [
            {"role": "system", "content": self.preamble_override},
            {"role": "user", "content": message}
        ]

        # Call Cohere Chat API
        response = co.chat(
            model=cohere_model_name,
            messages=messages,
            conversation_id=self.conversation_id,
            stream=False,
            temperature=0.3,
            return_chat_history=False,
            prompt_truncation='AUTO',
            citation_quality='fast',
            connectors=[{"id": "web-search"}],
        )

        # Extract AI text
        text = response.choices[0].message['content']

        # Extract citations (if any)
        result = ""
        if hasattr(response, "documents"):
            seen = set()
            for doc in response.documents:
                url = doc.get('url')
                if url and url not in seen:
                    seen.add(url)
                    result += f"\n\n{url}"

        return {"AI": text, "CITATIONS": result}


# Instantiate chatbot
chatbot = Chatbot()


def conversation(input: str, db: Session = Depends(get_db), current_user: user = Depends(oauth.get_current_user)):
    print(f"User: {input}")
    response = chatbot.generate_response(input)

    print({"AI": response['AI'], "CITATIONS": response['CITATIONS']})
    return response
