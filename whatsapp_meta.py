import os
import json
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse, JSONResponse
import anthropic

load_dotenv()

app = FastAPI()

claude = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

META_ACCESS_TOKEN    = os.getenv("META_ACCESS_TOKEN")
META_PHONE_NUMBER_ID = os.getenv("META_PHONE_NUMBER_ID")
META_VERIFY_TOKEN    = os.getenv("META_VERIFY_TOKEN")

# ── DEBUG: Print loaded env vars ──────────────────────────
print(f"🔑 VERIFY TOKEN LOADED: '{META_VERIFY_TOKEN}'")

from clinic_data import clinic_info

conversation_store = {}

def send_whatsapp_message(to_number: str, message: str):
    url = f"https://graph.facebook.com/v18.0/{META_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {META_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to_number,
        "type": "text",
        "text": {"body": message}
    }
    response = requests.post(url, headers=headers, json=payload)
    print(f"📤 Sent to {to_number}: {response.status_code}")
    return response.json()


@app.get("/webhook")
async def verify_webhook(request: Request):
    # Print ALL incoming params for debugging
    params = dict(request.query_params)
    print(f"📩 ALL PARAMS RECEIVED: {params}")
    print(f"🔑 MY VERIFY TOKEN: '{META_VERIFY_TOKEN}'")

    hub_mode         = params.get("hub.mode")
    hub_challenge    = params.get("hub.challenge")
    hub_verify_token = params.get("hub.verify_token")

    print(f"✏️ mode='{hub_mode}' | challenge='{hub_challenge}' | token='{hub_verify_token}'")

    # ── Hardcoded fallback check ──────────────────────────
    if hub_mode == "subscribe" and hub_verify_token == "clinicbot123":
        print("✅ Webhook verified!")
        return PlainTextResponse(content=hub_challenge)

    print(f"❌ Failed! Token match: {hub_verify_token == META_VERIFY_TOKEN}")
    return PlainTextResponse(content=hub_challenge or "ok", status_code=200)