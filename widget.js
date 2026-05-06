(function () {
  const CHAT_API = "https://web-production-6c14e.up.railway.app"; // Change to Railway URL in production
  const SESSION_ID = "session_" + Math.random().toString(36).substr(2, 9);

  // ── Inject Google Fonts ──────────────────────────────────
  const fontLink = document.createElement("link");
  fontLink.rel = "stylesheet";
  fontLink.href = "https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&family=DM+Serif+Display&display=swap";
  document.head.appendChild(fontLink);

  // ── Inject CSS ───────────────────────────────────────────
  const style = document.createElement("style");
  style.textContent = `
    #clinic-chat-btn {
      position: fixed; bottom: 28px; right: 28px;
      width: 64px; height: 64px;
      background: linear-gradient(135deg, #0f4c81 0%, #1a7f64 100%);
      border-radius: 50%;
      display: flex; align-items: center; justify-content: center;
      font-size: 30px; cursor: pointer;
      box-shadow: 0 4px 24px rgba(15,76,129,0.45);
      z-index: 999999;
      transition: transform 0.25s cubic-bezier(.34,1.56,.64,1), box-shadow 0.2s;
      user-select: none;
    }
    #clinic-chat-btn:hover {
      transform: scale(1.12);
      box-shadow: 0 8px 32px rgba(15,76,129,0.55);
    }
    #clinic-chat-btn.open { transform: rotate(90deg) scale(0.92); }

    #clinic-chat-window {
      position: fixed; bottom: 108px; right: 28px;
      width: 370px; height: 580px;
      background: #fff;
      border-radius: 24px;
      box-shadow: 0 12px 48px rgba(15,76,129,0.18);
      z-index: 999998;
      display: flex; flex-direction: column;
      overflow: hidden;
      transform: scale(0.85) translateY(30px);
      opacity: 0;
      pointer-events: none;
      transition: transform 0.3s cubic-bezier(.34,1.56,.64,1), opacity 0.25s;
      font-family: 'DM Sans', sans-serif;
    }
    #clinic-chat-window.open {
      transform: scale(1) translateY(0);
      opacity: 1;
      pointer-events: all;
    }

    .clinic-header {
      background: linear-gradient(135deg, #0f4c81 0%, #1a7f64 100%);
      padding: 16px 20px;
      display: flex; align-items: center; gap: 12px;
      position: relative;
    }
    .clinic-header-avatar {
      width: 42px; height: 42px; border-radius: 50%;
      background: rgba(255,255,255,0.2);
      display: flex; align-items: center; justify-content: center;
      font-size: 22px; flex-shrink: 0;
    }
    .clinic-header-info { flex: 1; }
    .clinic-header-name {
      font-family: 'DM Serif Display', serif;
      color: #fff; font-size: 15px; font-weight: 400; margin: 0;
    }
    .clinic-header-status {
      color: rgba(255,255,255,0.8); font-size: 11px;
      display: flex; align-items: center; gap: 5px; margin-top: 2px;
    }
    .clinic-status-dot {
      width: 7px; height: 7px; background: #4ade80;
      border-radius: 50%;
      animation: clinicPulse 2s infinite;
    }
    @keyframes clinicPulse {
      0%,100% { opacity:1; transform:scale(1); }
      50% { opacity:0.6; transform:scale(0.85); }
    }
    .clinic-close-btn {
      color: rgba(255,255,255,0.8); cursor: pointer;
      font-size: 20px; line-height: 1;
      transition: color 0.2s;
    }
    .clinic-close-btn:hover { color: #fff; }

    .clinic-messages {
      flex: 1; overflow-y: auto; padding: 16px;
      display: flex; flex-direction: column; gap: 12px;
      background: #f8faff;
      scrollbar-width: thin; scrollbar-color: #e0e0e0 transparent;
    }
    .clinic-messages::-webkit-scrollbar { width: 4px; }
    .clinic-messages::-webkit-scrollbar-thumb { background: #e0e0e0; border-radius: 4px; }

    .clinic-msg {
      display: flex; gap: 8px; align-items: flex-end;
      animation: clinicFadeIn 0.3s ease;
    }
    @keyframes clinicFadeIn {
      from { opacity:0; transform:translateY(8px); }
      to   { opacity:1; transform:translateY(0); }
    }
    .clinic-msg.user { flex-direction: row-reverse; }
    .clinic-msg-avatar {
      width: 28px; height: 28px; border-radius: 50%;
      background: linear-gradient(135deg, #0f4c81, #1a7f64);
      display: flex; align-items: center; justify-content: center;
      font-size: 14px; flex-shrink: 0;
    }
    .clinic-msg-bubble {
      max-width: 78%; padding: 10px 14px;
      border-radius: 18px; font-size: 13.5px; line-height: 1.5;
      color: #1a1a2e;
    }
    .clinic-msg.bot .clinic-msg-bubble {
      background: #fff;
      border-bottom-left-radius: 4px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.07);
    }
    .clinic-msg.user .clinic-msg-bubble {
      background: linear-gradient(135deg, #0f4c81, #1565c0);
      color: #fff;
      border-bottom-right-radius: 4px;
    }
    .clinic-msg-time {
      font-size: 10px; color: #9e9e9e; margin-top: 3px;
      text-align: right;
    }
    .clinic-msg.bot .clinic-msg-time { text-align: left; }

    .clinic-typing {
      display: flex; gap: 5px; padding: 12px 16px;
      background: #fff; border-radius: 18px; border-bottom-left-radius: 4px;
      width: fit-content;
      box-shadow: 0 2px 8px rgba(0,0,0,0.07);
    }
    .clinic-typing span {
      width: 7px; height: 7px; background: #0f4c81;
      border-radius: 50%;
      animation: clinicBounce 1.2s infinite;
    }
    .clinic-typing span:nth-child(2) { animation-delay: 0.2s; }
    .clinic-typing span:nth-child(3) { animation-delay: 0.4s; }
    @keyframes clinicBounce {
      0%,60%,100% { transform: translateY(0); }
      30% { transform: translateY(-6px); }
    }

    .clinic-quick-replies {
      display: flex; gap: 6px; flex-wrap: wrap; padding: 8px 16px 4px;
      background: #f8faff;
    }
    .clinic-quick-btn {
      background: #fff; border: 1.5px solid #e3f2fd;
      border-radius: 20px; padding: 5px 12px;
      font-size: 12px; color: #0f4c81; cursor: pointer;
      font-family: 'DM Sans', sans-serif; font-weight: 500;
      transition: all 0.2s; white-space: nowrap;
    }
    .clinic-quick-btn:hover {
      background: #0f4c81; color: #fff; border-color: #0f4c81;
    }

    .clinic-input-area {
      padding: 12px 16px;
      background: #fff;
      border-top: 1px solid #f0f0f0;
      display: flex; gap: 8px; align-items: center;
    }
    .clinic-input {
      flex: 1; border: 1.5px solid #e8f0fe;
      border-radius: 24px; padding: 9px 16px;
      font-size: 13.5px; font-family: 'DM Sans', sans-serif;
      outline: none; transition: border-color 0.2s;
      color: #1a1a2e;
    }
    .clinic-input:focus { border-color: #0f4c81; }
    .clinic-input::placeholder { color: #bdbdbd; }
    .clinic-send-btn {
      width: 38px; height: 38px;
      background: linear-gradient(135deg, #0f4c81, #1a7f64);
      border: none; border-radius: 50%; cursor: pointer;
      display: flex; align-items: center; justify-content: center;
      font-size: 16px; flex-shrink: 0;
      transition: transform 0.2s, box-shadow 0.2s;
    }
    .clinic-send-btn:hover {
      transform: scale(1.1);
      box-shadow: 0 4px 12px rgba(15,76,129,0.35);
    }
    .clinic-powered {
      text-align: center; font-size: 10px;
      color: #bdbdbd; padding: 4px;
      background: #fff; font-family: 'DM Sans', sans-serif;
    }

    @media (max-width: 480px) {
      #clinic-chat-window {
        width: calc(100vw - 24px);
        right: 12px; bottom: 90px;
        height: 70vh;
      }
    }
  `;
  document.head.appendChild(style);

  // ── Build HTML ───────────────────────────────────────────
  const btn = document.createElement("div");
  btn.id = "clinic-chat-btn";
  btn.innerHTML = "🏥";

  const win = document.createElement("div");
  win.id = "clinic-chat-window";
  win.innerHTML = `
    <div class="clinic-header">
      <div class="clinic-header-avatar">🏥</div>
      <div class="clinic-header-info">
        <p class="clinic-header-name">Bengaluru Health Clinic</p>
        <div class="clinic-header-status">
          <div class="clinic-status-dot"></div> AI Assistant • Available 24/7
        </div>
      </div>
      <div class="clinic-close-btn" id="clinic-close">✕</div>
    </div>

    <div class="clinic-messages" id="clinic-messages"></div>

    <div class="clinic-quick-replies" id="clinic-quick">
      <button class="clinic-quick-btn">🕐 Timings</button>
      <button class="clinic-quick-btn">👨‍⚕️ Doctors</button>
      <button class="clinic-quick-btn">💰 Fees</button>
      <button class="clinic-quick-btn">📅 Appointments</button>
    </div>

    <div class="clinic-input-area">
      <input class="clinic-input" id="clinic-input"
        type="text" placeholder="Type your question..." />
      <button class="clinic-send-btn" id="clinic-send">➤</button>
    </div>
    <div class="clinic-powered">Powered by Claude AI</div>
  `;

  document.body.appendChild(btn);
  document.body.appendChild(win);

  // ── Logic ────────────────────────────────────────────────
  const messagesEl = document.getElementById("clinic-messages");
  const inputEl    = document.getElementById("clinic-input");
  let isOpen = false;

  function getTime() {
    return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  }

  function parseMarkdown(text) {
  return text    
  // ── Remove table separator rows ───────────────────────
    .replace(/\|[-:| ]+\|\n?/g, "")
    // ── Tables ────────────────────────────────────────────
    .replace(/^\|(.+)\|$/gm, function(match) {
      const cells = match.split("|").filter(c => c.trim());
      if (!cells.length) return "";
      return "<tr>" + cells.map(c =>
        `<td style="padding:7px 12px;border:1px solid #e3f2fd;font-size:12.5px;vertical-align:middle;background:#fff">${c.trim()}</td>`
      ).join("") + "</tr>";
    })
    .replace(/(<tr>[\s\S]*?<\/tr>)+/g, match =>
      `<div style="overflow-x:auto;margin:8px 0"><table style="border-collapse:collapse;width:100%">${match}</table></div>`
    )    
    // ── Headings ──────────────────────────────────────────
    .replace(/^### (.+)/gm, "<h4 style='font-size:13px;color:#0f4c81;margin:8px 0 4px;font-family:DM Serif Display,serif'>$1</h4>")
    .replace(/^## (.+)/gm, "<h3 style='font-size:14px;color:#0f4c81;margin:10px 0 4px;font-family:DM Serif Display,serif'>$1</h3>")
    .replace(/^# (.+)/gm, "<h2 style='font-size:16px;color:#0f4c81;margin:10px 0 6px;font-family:DM Serif Display,serif'>$1</h2>")
    // ── Bold ──────────────────────────────────────────────
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    // ── Italic ────────────────────────────────────────────
    .replace(/\*(.*?)\*/g, "<em>$1</em>")
    // ── Bullet points ─────────────────────────────────────
    .replace(/^[-•]\s(.+)/gm, "<li style='margin:4px 0;padding-left:4px'>$1</li>")
    .replace(/(<li.*<\/li>)/gs, match =>
      `<ul style="padding-left:16px;margin:6px 0">${match}</ul>`
    )
    // ── Numbered list ─────────────────────────────────────
    .replace(/^\d+\.\s(.+)/gm, "<li style='margin:4px 0'>$1</li>")
    // ── Divider ───────────────────────────────────────────
    .replace(/^---$/gm, "<hr style='border:none;border-top:1px solid #e3f2fd;margin:8px 0'>")
    // ── Line breaks ───────────────────────────────────────
    .replace(/\n/g, "<br>");
}

function addMessage(text, role) {
  const isUser = role === "user";
  const div = document.createElement("div");
  div.className = `clinic-msg ${isUser ? "user" : "bot"}`;
  div.innerHTML = `
    ${!isUser ? '<div class="clinic-msg-avatar">🤖</div>' : ""}
    <div>
      <div class="clinic-msg-bubble">${isUser ? text : parseMarkdown(text)}</div>
      <div class="clinic-msg-time">${getTime()}</div>
    </div>
    ${isUser ? '<div class="clinic-msg-avatar" style="background:linear-gradient(135deg,#1565c0,#0f4c81)">👤</div>' : ""}
  `;
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

  function showTyping() {
    const div = document.createElement("div");
    div.className = "clinic-msg bot";
    div.id = "clinic-typing";
    div.innerHTML = `
      <div class="clinic-msg-avatar">🤖</div>
      <div class="clinic-typing">
        <span></span><span></span><span></span>
      </div>`;
    messagesEl.appendChild(div);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function removeTyping() {
    const t = document.getElementById("clinic-typing");
    if (t) t.remove();
  }

  async function sendMessage(text) {
    if (!text.trim()) return;
    addMessage(text, "user");
    inputEl.value = "";
    document.getElementById("clinic-quick").style.display = "none";
    showTyping();

    try {
      const res = await fetch(`${CHAT_API}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text, session_id: SESSION_ID, client_id: "website" })
      });
      const data = await res.json();
      removeTyping();
      addMessage(data.reply, "bot");
    } catch (e) {
      removeTyping();
      addMessage("Sorry, I'm having difficulties. Please call 080-12345678.", "bot");
    }
  }

  // ── Welcome message ──────────────────────────────────────
  function showWelcome() {
    addMessage("👋 Hello! Welcome to **Bengaluru Health Clinic**.\n\nI'm your 24/7 AI assistant. How can I help you today?", "bot");
  }

  // ── Toggle chat ──────────────────────────────────────────
  btn.onclick = function () {
    isOpen = !isOpen;
    win.classList.toggle("open", isOpen);
    btn.classList.toggle("open", isOpen);
    btn.innerHTML = isOpen ? "✕" : "🏥";
    if (isOpen && messagesEl.children.length === 0) showWelcome();
  };

  document.getElementById("clinic-close").onclick = function () {
    isOpen = false;
    win.classList.remove("open");
    btn.classList.remove("open");
    btn.innerHTML = "🏥";
  };

  // ── Send button & Enter key ──────────────────────────────
  document.getElementById("clinic-send").onclick = () => sendMessage(inputEl.value);
  inputEl.addEventListener("keypress", e => { if (e.key === "Enter") sendMessage(inputEl.value); });

  // ── Quick reply buttons ──────────────────────────────────
  document.querySelectorAll(".clinic-quick-btn").forEach(b => {
    b.onclick = () => sendMessage(b.textContent.replace(/^[^\w]+/, "").trim());
  });

})();