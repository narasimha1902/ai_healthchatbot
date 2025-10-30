# Placeholder for Ada Health model integration
class AdaHealthModel:
    def __init__(self):
        pass

    def chat(self, input: str, db: Session = None, current_user: user = None):
        """
        Placeholder for Ada Health API integration.
        Replace this with actual API call to Ada Health.
        """
        # TODO: Implement Ada Health API call here
        ai_text = "[Ada Health] This is a placeholder response for Ada Health queries."
        return {"AI": ai_text, "CITATIONS": ""}
# llama.py
from sqlalchemy.orm import Session
from fastapi import FastAPI, APIRouter, status, Depends, HTTPException
from typing import Optional
import cohere
from database.db import get_db
from decouple import config
from services.cohere import conversation as old_conversation
from services.gemini import run
from schema.users_shema import user
from schema.llm_schema import choose, search
import oauth

fastapp = FastAPI()
app = APIRouter(tags=["Llama"])
fastapp.include_router(app)

# Load Cohere API key
COHERE_API_KEY = config("CohereAPI")
co = cohere.Client(COHERE_API_KEY)



# Placeholder for custom health-focused LLM

# HealthLLM loads and uses the trained health query model
import os
import json
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification
import torch

class HealthLLM:
    def __init__(self):
        model_dir = './health_llm_model'
        if os.path.exists(model_dir):
            self.tokenizer = DistilBertTokenizerFast.from_pretrained(model_dir)
            self.model = DistilBertForSequenceClassification.from_pretrained(model_dir)
            with open(os.path.join(model_dir, 'answers.json'), 'r') as f:
                self.answers = json.load(f)
        else:
            self.tokenizer = None
            self.model = None
            self.answers = ["Model not trained. Please run train_health_llm.py."]

    def chat(self, input: str, db: Session = None, current_user: user = None):
        if self.model is None or self.tokenizer is None:
            ai_text = self.answers[0]
            return {"AI": ai_text, "CITATIONS": ""}
        inputs = self.tokenizer(input, return_tensors="pt", truncation=True, padding='max_length', max_length=32)
        with torch.no_grad():
            outputs = self.model(**inputs)
            pred = torch.argmax(outputs.logits, dim=1).item()
            ai_text = self.answers[pred]
        return {"AI": ai_text, "CITATIONS": ""}


class Choose:
    def __init__(self):
        self.running_model = None


    def model(self, user_choice: str = None):
        # Always use HealthLLM as the default model
        self.running_model = HealthLLM().chat
        return self.running_model

    def current_model(self):
        if self.running_model is None:
            raise HTTPException(status_code=400, detail="Model not set")
        return self.running_model

    # New Cohere chat API function
    def cohere_chat(self, input: str, db: Session = None, current_user: user = None):
        """
        Handles input for Cohere chat API.
        """
        # Build conversation history (optional: can store/retrieve from DB)
        history = [{"role": "user", "content": input}]

        try:
            response = co.chat(
                model="command-r",
                messages=history
            )
            ai_text = response.text
            # Return in same format as old_conversation
            return {"AI": ai_text, "CITATIONS": ""}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Cohere API error: {str(e)}")


# Initialize model manager
model_manager = Choose()

def model_choice():
    return model_manager


# Choose model Endpoint
@app.post("/choose_model/")
async def choose_model(
    choice: choose, 
    manager: Choose = Depends(model_choice), 
    current_user: user = Depends(oauth.get_current_user)
):
    user_choose = manager.model(choice)
    return {'message': status.HTTP_200_OK, "Detail": f"{user_choose} is now live"}


# Conversation Endpoint
@app.post("/response/")
async def conversationing(
    input: str,
    choice: search = None,
    manager: Choose = Depends(model_choice),
    db: Session = Depends(get_db),
    current_user: user = Depends(oauth.get_current_user)
):
    model = manager.current_model()

    if model == old_conversation or model == manager.cohere_chat:
        # Pass input to Cohere chat API
        result = model(input=input, db=db, current_user=current_user)
    elif model == run:
        # Google Gemini AI
        if not choice:
            raise HTTPException(status_code=400, detail="Choice parameter is required for the Google Gemini AI model")
        result = model(input=input, choice=choice, db=db, current_user=current_user)
    else:
        raise HTTPException(status_code=400, detail="Unknown AI model")

    return {'message': status.HTTP_200_OK, "Detail": result}
