import os
from dotenv import load_dotenv
from fastapi import FastAPI, Form
from fastapi.responses import PlainTextResponse
from twilio.twiml.messaging_response import MessagingResponse
import anthropic
from database import init_db, save_message

load_dotenv()

app = FastAPI()

claude = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

from clinic_data import clinic_info

# ── Initialize database on startup ────────────────────────
init_db()

# ── Conversation memory per user ──────────────────────────
conversation_store = {}

@app.post("/whatsapp", response_class=PlainTextResponse)
async def whatsapp_webhook(
    Body: str = Form(...),
    From: str = Form(...),
    To:   str = Form(...)
):
    patient_number  = From
    patient_message = Body.strip()

    print(f"\n📱 Message from {patient_number}: {patient_message}")

    # ── Save patient message to DB ────────────────────────
    save_message(
        phone   = patient_number,
        role    = "user",
        message = patient_message,
        channel = "whatsapp"
    )

    # ── Manage conversation history ───────────────────────
    if patient_number not in conversation_store:
        conversation_store[patient_number] = []

    conversation_store[patient_number].append({
        "role"    : "user",
        "content" : patient_message
    })

    recent_history = conversation_store[patient_number][-10:]

    # ── Get Claude response ───────────────────────────────
    try:
        response = claude.messages.create(
            model      = "claude-opus-4-5",
            max_tokens = 500,
            system     = clinic_info,
            messages   = recent_history
        )
        reply = response.content[0].text

    except Exception as e:
        print(f"❌ Claude error: {e}")
        reply = "Sorry, I'm having difficulties. Please call 080-12345678."

    # ── Save bot reply to DB ──────────────────────────────
    save_message(
        phone   = patient_number,
        role    = "assistant",
        message = reply,
        channel = "whatsapp"
    )

    conversation_store[patient_number].append({
        "role"    : "assistant",
        "content" : reply
    })

    print(f"🤖 Bot reply: {reply}")

    twilio_response = MessagingResponse()
    twilio_response.message(reply)
    return str(twilio_response)


@app.get("/")
def health_check():
    return {
        "status"               : "✅ Clinic WhatsApp Bot is Live!",
        "active_conversations" : len(conversation_store)
    }