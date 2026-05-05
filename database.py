import os
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

# ── Supabase client ───────────────────────────────────────
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def init_db():
    print("✅ Supabase connected!")

def save_message(phone: str, role: str, message: str, channel: str = "whatsapp"):
    supabase.table("conversations").insert({
        "phone"     : phone,
        "role"      : role,
        "message"   : message,
        "timestamp" : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "channel"   : channel
    }).execute()

def get_all_conversations():
    response = supabase.table("conversations")\
        .select("*")\
        .order("timestamp", desc=True)\
        .execute()
    return [(r["phone"], r["role"], r["message"], r["timestamp"], r["channel"])
            for r in response.data]

def get_conversation_by_phone(phone: str):
    response = supabase.table("conversations")\
        .select("*")\
        .eq("phone", phone)\
        .order("timestamp")\
        .execute()
    return [(r["role"], r["message"], r["timestamp"])
            for r in response.data]

def get_stats():
    all_data = supabase.table("conversations").select("*").execute().data

    total_messages = len(all_data)
    total_users    = len(set(r["phone"] for r in all_data))

    today = datetime.now().strftime("%Y-%m-%d")
    today_messages = len([r for r in all_data if r["timestamp"].startswith(today)])

    # Most active user
    from collections import Counter
    phone_counts = Counter(r["phone"] for r in all_data)
    most_active  = phone_counts.most_common(1)[0] if phone_counts else None

    return {
        "total_messages" : total_messages,
        "total_users"    : total_users,
        "today_messages" : today_messages,
        "most_active"    : most_active
    }

def delete_conversation(phone: str):
    supabase.table("conversations")\
        .delete()\
        .eq("phone", phone)\
        .execute()