import streamlit as st
from datetime import datetime
from chatbot import get_response
from clinic_data import clinic_info
from pdf_processor import extract_text_from_pdf, build_system_prompt

# ── Page config ──────────────────────────────────────────
st.set_page_config(
    page_title="Bengaluru Health Clinic",
    page_icon="🏥",
    layout="centered"
)

# ── Custom CSS ───────────────────────────────────────────
st.markdown("""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Serif+Display&display=swap');

/* ── Global ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* ── Hide Streamlit default elements ── */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* ── Main background ── */
.stApp {
    background: linear-gradient(135deg, #f0f7ff 0%, #ffffff 50%, #f0fdf4 100%);
}

/* ── Hero header ── */
.clinic-hero {
    background: linear-gradient(135deg, #0f4c81 0%, #1a7f64 100%);
    border-radius: 20px;
    padding: 28px 32px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    gap: 20px;
    box-shadow: 0 8px 32px rgba(15, 76, 129, 0.25);
    position: relative;
    overflow: hidden;
}

.clinic-hero::before {
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 180px; height: 180px;
    background: rgba(255,255,255,0.06);
    border-radius: 50%;
}

.clinic-hero::after {
    content: '';
    position: absolute;
    bottom: -60px; left: 60px;
    width: 220px; height: 220px;
    background: rgba(255,255,255,0.04);
    border-radius: 50%;
}

.hero-icon {
    font-size: 52px;
    filter: drop-shadow(0 4px 8px rgba(0,0,0,0.2));
    z-index: 1;
}

.hero-text { z-index: 1; }

.hero-title {
    font-family: 'DM Serif Display', serif;
    font-size: 26px;
    color: #ffffff;
    margin: 0;
    line-height: 1.2;
    letter-spacing: -0.3px;
}

.hero-subtitle {
    font-size: 13px;
    color: rgba(255,255,255,0.75);
    margin: 4px 0 0 0;
    font-weight: 400;
    letter-spacing: 0.3px;
}

.hero-badge {
    margin-left: auto;
    background: rgba(255,255,255,0.15);
    border: 1px solid rgba(255,255,255,0.25);
    border-radius: 20px;
    padding: 6px 14px;
    color: #ffffff;
    font-size: 12px;
    font-weight: 600;
    z-index: 1;
    backdrop-filter: blur(10px);
}

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
    border-radius: 16px !important;
    padding: 12px 16px !important;
    margin-bottom: 8px !important;
    border: none !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
}

/* User message */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: linear-gradient(135deg, #0f4c81, #1565c0) !important;
    color: white !important;
    margin-left: 40px !important;
}

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) p {
    color: white !important;
}

/* Assistant message */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
    background: #ffffff !important;
    border: 1px solid #e8f0fe !important;
    margin-right: 40px !important;
}

/* ── Chat input ── */
[data-testid="stChatInput"] {
    border-radius: 16px !important;
    border: 2px solid #e8f0fe !important;
    box-shadow: 0 4px 20px rgba(15, 76, 129, 0.1) !important;
    background: #ffffff !important;
}

[data-testid="stChatInput"]:focus-within {
    border-color: #0f4c81 !important;
    box-shadow: 0 4px 24px rgba(15, 76, 129, 0.2) !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f4c81 0%, #0d3d66 100%) !important;
}

[data-testid="stSidebar"] * {
    color: white !important;
}

[data-testid="stSidebar"] .stButton button {
    background: rgba(255,255,255,0.12) !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    color: white !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
    transition: all 0.2s !important;
}

[data-testid="stSidebar"] .stButton button:hover {
    background: rgba(255,255,255,0.22) !important;
    transform: translateY(-1px) !important;
}

/* Info cards in sidebar */
[data-testid="stSidebar"] [data-testid="stAlert"] {
    background: rgba(255,255,255,0.1) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 10px !important;
    color: white !important;
}

/* File uploader */
[data-testid="stSidebar"] [data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.08) !important;
    border: 2px dashed rgba(255,255,255,0.3) !important;
    border-radius: 12px !important;
    padding: 8px !important;
}

/* Divider */
[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.15) !important;
}

/* ── Quick action pills ── */
.quick-actions {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-bottom: 20px;
}

.quick-pill {
    background: #ffffff;
    border: 1.5px solid #e8f0fe;
    border-radius: 20px;
    padding: 6px 14px;
    font-size: 12px;
    font-weight: 500;
    color: #0f4c81;
    cursor: pointer;
    transition: all 0.2s;
    white-space: nowrap;
    box-shadow: 0 2px 6px rgba(15, 76, 129, 0.08);
}

.quick-pill:hover {
    background: #0f4c81;
    color: white;
    border-color: #0f4c81;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(15, 76, 129, 0.2);
}

/* ── Status bar ── */
.status-bar {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 16px;
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    border-radius: 10px;
    margin-bottom: 16px;
    font-size: 13px;
    color: #15803d;
    font-weight: 500;
}

.status-dot {
    width: 8px;
    height: 8px;
    background: #22c55e;
    border-radius: 50%;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.6; transform: scale(0.85); }
}
            /* ── File uploader button fix ── */
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInput"] + div button,
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] {
    background: #ffffff !important;
    color: #0f4c81 !important;
    border: 2px solid #ffffff !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 6px 16px !important;
}

[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"]:hover {
    background: #e8f0fe !important;
    color: #0f4c81 !important;
    transform: translateY(-1px) !important;
}

/* ── Uploader dropzone area ── */
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
    background: rgba(255,255,255,0.12) !important;
    border: 2px dashed rgba(255,255,255,0.5) !important;
    border-radius: 12px !important;
}

[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] p,
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] span {
    color: rgba(255,255,255,0.85) !important;
}
</style>
""", unsafe_allow_html=True)

# ── Hero Header ─────────────────────────────────────────
st.markdown("""
<div class="clinic-hero">
    <div class="hero-icon">🏥</div>
    <div class="hero-text">
        <p class="hero-title">Bengaluru Health Clinic</p>
        <p class="hero-subtitle">AI-Powered Patient Assistant • Available 24/7</p>
    </div>
    <div class="hero-badge">● Online</div>
</div>
""", unsafe_allow_html=True)

# ── Status Bar ───────────────────────────────────────────
st.markdown("""
<div class="status-bar">
    <div class="status-dot"></div>
    AI Assistant is ready — Ask me anything about the clinic!
</div>
""", unsafe_allow_html=True)

# ── Quick Action Pills ────────────────────────────────────
st.markdown("""
<div class="quick-actions">
    <div class="quick-pill">🕐 Timings</div>
    <div class="quick-pill">👨‍⚕️ Doctors</div>
    <div class="quick-pill">💰 Fees</div>
    <div class="quick-pill">📅 Appointments</div>
    <div class="quick-pill">🧪 Lab Tests</div>
    <div class="quick-pill">🏥 Insurance</div>
</div>
""", unsafe_allow_html=True)

# ── Initialize session state ──────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant",
        "content": f"👋 **Hello! Welcome to Bengaluru Health Clinic.**\n\nToday is **{datetime.now().strftime('%A, %d %B %Y')}**\n\nI'm your AI-powered assistant, here to help you 24/7. You can ask me about:\n\n- 🕐 **Clinic timings** & holidays\n- 👨‍⚕️ **Doctors** & their availability\n- 💰 **Fees** & payment options\n- 🗓️ **Booking** an appointment\n- 🧪 **Lab tests** & reports\n- 🏥 **Insurance** we accept\n\n📄 You can also **upload a clinic PDF** from the sidebar!\n\nHow can I help you today?"
    })

if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = None

if "pdf_name" not in st.session_state:
    st.session_state.pdf_name = None

# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🏥 Bengaluru Health Clinic")
    st.markdown("---")

    st.markdown("##### 📍 Contact & Location")
    st.info("📞 080-12345678")
    st.info("⏰ Mon–Sat: 9AM – 8PM")
    st.info("📍 MG Road, Bengaluru")
    st.markdown("---")

    st.markdown("##### 📄 Upload Clinic Document")
    st.caption("Upload any clinic PDF — brochure, FAQ, price list")

    uploaded_file = st.file_uploader(
        "Choose a PDF",
        type=["pdf"],
        label_visibility="collapsed"
    )

    if uploaded_file is not None:
        if st.session_state.pdf_name != uploaded_file.name:
            with st.spinner("📖 Reading document..."):
                pdf_text = extract_text_from_pdf(uploaded_file)
                st.session_state.pdf_text = pdf_text
                st.session_state.pdf_name = uploaded_file.name
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"📄 I've successfully read **{uploaded_file.name}**!\n\nYou can now ask me any questions from this document."
                })
            st.success(f"✅ {uploaded_file.name}")

    if st.session_state.pdf_name:
        st.caption(f"📎 Active: {st.session_state.pdf_name}")
        if st.button("❌ Remove PDF", use_container_width=True):
            st.session_state.pdf_text = None
            st.session_state.pdf_name = None
            st.rerun()

    st.markdown("---")
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.caption("Powered by Claude AI • © 2026 Bengaluru Health Clinic")

# ── Build system prompt ───────────────────────────────────
system_prompt = build_system_prompt(clinic_info, st.session_state.pdf_text)

# ── Display chat history ──────────────────────────────────
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ── User input ────────────────────────────────────────────
if user_input := st.chat_input("Type your question here..."):

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

# Get Claude response
with st.chat_message("assistant"):
    with st.spinner("Typing..."):
        api_messages = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ]
        response = get_response(api_messages, system_prompt)
        st.markdown(response)

# Save to database
try:
    from database import save_message
    save_message("webchat", "user", user_input, "webchat")
    save_message("webchat", "assistant", response, "webchat")
except Exception as e:
    print(f"DB save error: {e}")

# Save response
st.session_state.messages.append({
    "role": "assistant",
    "content": response
})