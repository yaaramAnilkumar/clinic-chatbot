import streamlit as st
import pandas as pd
from database import (
    init_db,
    get_all_conversations,
    get_conversation_by_phone,
    get_stats,
    delete_conversation
)

# ── Page config ───────────────────────────────────────────
st.set_page_config(
    page_title = "Clinic Chat Dashboard",
    page_icon  = "📊",
    layout     = "wide"
)

# ── Initialize DB ─────────────────────────────────────────
init_db()

# ── Header ────────────────────────────────────────────────
st.title("📊 Clinic Chat History Dashboard")
st.caption("Monitor all WhatsApp conversations in real-time")
st.divider()

# ── Stats Row ─────────────────────────────────────────────
stats = get_stats()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("💬 Total Messages", stats["total_messages"])

with col2:
    st.metric("👥 Unique Patients", stats["total_users"])

with col3:
    st.metric("📅 Today's Messages", stats["today_messages"])

with col4:
    if stats["most_active"]:
        phone = stats["most_active"][0].replace("whatsapp:+91", "+91-")
        st.metric("🏆 Most Active", phone)
    else:
        st.metric("🏆 Most Active", "N/A")

st.divider()

# ── All Conversations Table ───────────────────────────────
st.subheader("📋 All Conversations")

rows = get_all_conversations()

if not rows:
    st.info("💬 No conversations yet — start chatting on WhatsApp!")
else:
    df = pd.DataFrame(rows, columns=["Phone", "Role", "Message", "Time", "Channel"])
    df["Phone"] = df["Phone"].str.replace("whatsapp:", "")
    df["Role"]  = df["Role"].map({"user": "👤 Patient", "assistant": "🤖 Bot"})

    # ── Filters ───────────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        phones    = ["All"] + list(df["Phone"].unique())
        filter_ph = st.selectbox("Filter by Phone", phones)

    with col2:
        roles     = ["All", "👤 Patient", "🤖 Bot"]
        filter_ro = st.selectbox("Filter by Role", roles)

    # Apply filters
    filtered = df.copy()
    if filter_ph != "All":
        filtered = filtered[filtered["Phone"] == filter_ph]
    if filter_ro != "All":
        filtered = filtered[filtered["Role"] == filter_ro]

    st.dataframe(
        filtered,
        use_container_width = True,
        height              = 400
    )

    st.caption(f"Showing {len(filtered)} of {len(df)} total messages")

st.divider()

# ── Individual Conversation Viewer ────────────────────────
st.subheader("💬 View Full Conversation")

if rows:
    all_phones  = list(set([r[0].replace("whatsapp:", "") for r in rows]))
    sel_phone   = st.selectbox("Select Patient Number", all_phones)

    if sel_phone:
        convo = get_conversation_by_phone(f"whatsapp:{sel_phone}")

        if convo:
            for role, message, timestamp in convo:
                if role == "user":
                    with st.chat_message("user"):
                        st.markdown(f"**{timestamp}**")
                        st.markdown(message)
                else:
                    with st.chat_message("assistant"):
                        st.markdown(f"**{timestamp}**")
                        st.markdown(message)

        # ── Delete conversation ────────────────────────────
        st.divider()
        if st.button(f"🗑️ Delete conversation with {sel_phone}", type="secondary"):
            delete_conversation(f"whatsapp:{sel_phone}")
            st.success("✅ Conversation deleted!")
            st.rerun()

# ── Refresh button ────────────────────────────────────────
st.divider()
if st.button("🔄 Refresh Data", type="primary"):
    st.rerun()