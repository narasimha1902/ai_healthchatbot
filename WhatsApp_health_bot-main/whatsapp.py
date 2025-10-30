# Simple ping endpoint for debugging
@app.get('/ping')
async def ping():
    return {"status": "ok", "message": "WhatsApp router is working!"}
# whatsapp.py
from fastapi import APIRouter, Request, status, Depends
from sqlalchemy.orm import Session
from services.twilio import send_message
import llama
from database.db import get_db

app = APIRouter(tags=["WhatsApp"])

# Debug route
@app.get('/testing/')
async def home():
    return {"Message": "Debugger TESTING----"}

# Global state for AI choice
chosen = None
choice = None

@app.post("/twilio/")
async def twilio_webhook(
    request: Request, 
    manager: llama.Choose = Depends(llama.model_choice), 
    db: Session = Depends(get_db)
):
    global chosen, choice
    sending_message = None

    provide = await request.form()
    input_text = provide.get('Body')
    sender_id = provide.get('From')

    print(f"Incoming from {sender_id}: {input_text}")

    # Initial thinking message
    send_message(sender_id, "Thinking...")

    # Reset conversation
    if input_text.lower() == "start over":
        chosen = None
        choice = None
        sending_message = "Chat restarted. Please choose 'diagnosis' or 'health tip'."
        send_message(sender_id, sending_message)
        return {"message": status.HTTP_200_OK, "Detail": sending_message}

    # Choose AI model if not already chosen
    if chosen not in ["Cohere large AI", "Google Gemini AI"]:
        chosen = await whatsapp_choose(choice=input_text, current_user=sender_id, manager=manager)
        if chosen == "Cohere large AI":
            sending_message = "Ready to assist! What questions do you have for me?"
        elif chosen == "Google Gemini AI":
            sending_message = "I'm happy to assist you. Could you describe any health concerns you're experiencing?"
        else:
            sending_message = chosen
        choice = "Google search"
        send_message(sender_id, sending_message)
        return {"message": status.HTTP_200_OK, "Detail": sending_message}

    # If AI model already chosen, process user input through AI
    if chosen in ["Cohere large AI", "Google Gemini AI"]:
        response = await llama.conversationing(
            input=input_text,
            choice=choice,
            manager=manager,
            db=db,
            current_user=sender_id
        )

        sending_message = response['Detail']["AI"]
        sending_citation = f"Source:\n\n{response['Detail']['CITATIONS']}"

        print(f"Reply: {sending_message}")
        print(f"Citations: {sending_citation}")

        # Send AI response
        send_message(sender_id, sending_message)

        # Send citations if available
        if response['Detail']["CITATIONS"]:
            send_message(sender_id, sending_citation)

    return {"message": status.HTTP_200_OK, "Detail": sending_message}


# Function to choose AI model
async def whatsapp_choose(choice, current_user, manager: llama.Choose = Depends(llama.model_choice)):
    choice_lower = choice.lower() if choice else ""

    if "diagnosis" in choice_lower:
        ai_choice = "Google Gemini AI"
    elif "tip" in choice_lower or "resources" in choice_lower:
        ai_choice = "Cohere large AI"
    else:
        ai_choice = None

    if ai_choice not in ["Cohere large AI", "Google Gemini AI"]:
        user_prompt = (
            "Hello! Would you prefer a comprehensive health diagnosis or a health tip with useful resources? \n\n"
            "Kindly respond with 'diagnosis' for a detailed health assessment or 'health tip' for a quick health tip and resources."
        )
        send_message(current_user, user_prompt)
        return None

    chosen_result = await llama.choose(choice=ai_choice, manager=manager, current_user=current_user)
    return chosen_result
