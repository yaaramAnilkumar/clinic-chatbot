import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import anthropic
from dotenv import load_dotenv
from clinic_data import clinic_info
from database import save_message, init_db

load_dotenv()

app = FastAPI()

# ── Allow any website to call your API ───────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Serve static files (widget.js) ───────────────────────
app.mount("/static", StaticFiles(directory="."), name="static")

claude = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# ── Initialize DB ─────────────────────────────────────────
init_db()

# ── Session memory ────────────────────────────────────────
sessions = {}

class ChatRequest(BaseModel):
    message:    str
    session_id: str = "default"
    client_id:  str = "website"

@app.post("/chat")
async def chat(request: ChatRequest):
    sid = f"{request.client_id}_{request.session_id}"

    if sid not in sessions:
        sessions[sid] = []

    sessions[sid].append({
        "role":    "user",
        "content": request.message
    })

    try:
        response = claude.messages.create(
            model      = "claude-sonnet-4-6",
            max_tokens = 500,
            system     = clinic_info,
            messages   = sessions[sid][-10:]
        )
        reply = response.content[0].text
    except Exception as e:
        reply = "Sorry, I'm having difficulties. Please call 080-12345678."

    sessions[sid].append({
        "role":    "assistant",
        "content": reply
    })

    # ── Save to database ──────────────────────────────────
    try:
        save_message(f"web_{request.session_id}", "user",      request.message, "website")
        save_message(f"web_{request.session_id}", "assistant", reply,           "website")
    except:
        pass

    return {
        "reply":      reply,
        "session_id": request.session_id
    }

@app.get("/widget.js")
def serve_widget():
    return FileResponse("widget.js", media_type="application/javascript")

@app.get("/")
def health():
    return {"status": "✅ Chatbot API is running!"}