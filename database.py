import sqlite3
from datetime import datetime

DB_PATH = "chat_history.db"

def init_db():
    """Create database and tables if they don't exist"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            phone       TEXT NOT NULL,
            role        TEXT NOT NULL,
            message     TEXT NOT NULL,
            timestamp   TEXT NOT NULL,
            channel     TEXT DEFAULT 'whatsapp'
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ Database initialized!")


def save_message(phone: str, role: str, message: str, channel: str = "whatsapp"):
    """Save a single message to database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO conversations (phone, role, message, timestamp, channel)
        VALUES (?, ?, ?, ?, ?)
    """, (
        phone,
        role,
        message,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        channel
    ))
    
    conn.commit()
    conn.close()


def get_all_conversations():
    """Get all conversations grouped by phone number"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT phone, role, message, timestamp, channel
        FROM conversations
        ORDER BY timestamp DESC
    """)
    
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_conversation_by_phone(phone: str):
    """Get full conversation for a specific phone number"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT role, message, timestamp
        FROM conversations
        WHERE phone = ?
        ORDER BY timestamp ASC
    """, (phone,))
    
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_stats():
    """Get summary statistics"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Total messages
    cursor.execute("SELECT COUNT(*) FROM conversations")
    total_messages = cursor.fetchone()[0]

    # Total unique users
    cursor.execute("SELECT COUNT(DISTINCT phone) FROM conversations")
    total_users = cursor.fetchone()[0]

    # Today's messages
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("""
        SELECT COUNT(*) FROM conversations
        WHERE timestamp LIKE ?
    """, (f"{today}%",))
    today_messages = cursor.fetchone()[0]

    # Most active user
    cursor.execute("""
        SELECT phone, COUNT(*) as count
        FROM conversations
        GROUP BY phone
        ORDER BY count DESC
        LIMIT 1
    """)
    most_active = cursor.fetchone()

    conn.close()

    return {
        "total_messages" : total_messages,
        "total_users"    : total_users,
        "today_messages" : today_messages,
        "most_active"    : most_active
    }


def delete_conversation(phone: str):
    """Delete all messages for a phone number"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM conversations WHERE phone = ?", (phone,))
    conn.commit()
    conn.close()