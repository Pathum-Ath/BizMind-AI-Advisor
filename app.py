import streamlit as st
from agent import build_agent, get_welcome_message
from memory import (
    init_session, add_message, get_messages,
    update_profile, get_profile_summary,
    clear_session, KEY_AGENT,
)
from utils import (
    extract_context, analyse_sales,
    format_prompt,
)
from langchain_core.messages import HumanMessage, AIMessage

st.set_page_config(
    page_title="BizMind – AI Business Advisor",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&display=swap');

:root {
    --bg:        #07080d;
    --bg2:       #0d0f18;
    --bg3:       #12151f;
    --surface:   #181c28;
    --border:    rgba(255,255,255,0.07);
    --accent:    #6c63ff;
    --accent2:   #ff6584;
    --accent3:   #43e8b0;
    --text:      #e8eaf6;
    --muted:     #6b7280;
    --user-bg:   #1e2235;
    --ai-bg:     #111420;
    --glow:      rgba(108,99,255,0.18);
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background: #fff0f5!important;
    color: var(--text) !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--accent); border-radius: 999px; }

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* ══════════════════════════════════════════
   SIDEBAR
══════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: #1e2235 !important;
    border-right: 1px solid var(--border) !important;
    padding: 0 !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding: 1.5rem 1.2rem !important;
}

.sidebar-logo {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 1.8rem;
}
.sidebar-logo-icon {
    width: 36px; height: 36px;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px;
    box-shadow: 0 0 20px var(--glow);
}
.sidebar-logo-text {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 1.3rem;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.5px;
}
.sidebar-tagline {
    font-size: 0.7rem;
    color: var(--muted);
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-top: -1.4rem;
    margin-bottom: 1.5rem;
    padding-left: 46px;
}

.section-label {
    font-family: 'Syne', sans-serif;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 0.6rem;
    margin-top: 1.4rem;
}

/* API Key input */
[data-testid="stTextInput"] input {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.85rem !important;
    padding: 0.55rem 0.9rem !important;
    transition: border 0.2s, box-shadow 0.2s !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--glow) !important;
    outline: none !important;
}

/* Profile card */
.profile-card {
    background: #ff6584;
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 0.9rem 1rem;
    font-size: 0.82rem;
    line-height: 1.8;
}
.profile-card b { color: var(--accent3); font-weight: 500; }
.profile-empty {
    color: var(--muted);
    font-size: 0.78rem;
    font-style: italic;
    text-align: center;
    padding: 0.6rem 0;
}

/* Quick action buttons */
[data-testid="stButton"] > button {
    width: 100% !important;
    background: var(--surface) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    padding: 0.55rem 0.9rem !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    text-align: left !important;
    margin-bottom: 0.35rem !important;
    transition: all 0.2s ease !important;
    cursor: pointer !important;
}
[data-testid="stButton"] > button:hover {
    background: var(--accent) !important;
    border-color: var(--accent) !important;
    transform: translateX(3px) !important;
    box-shadow: 0 4px 20px var(--glow) !important;
    color: white !important;
}

/* New chat button */
[data-testid="stButton"] > button[kind="secondary"] {
    background: transparent !important;
    border: 1px solid var(--accent2) !important;
    color: var(--accent2) !important;
    text-align: center !important;
}
[data-testid="stButton"] > button[kind="secondary"]:hover {
    background: var(--accent2) !important;
    color: white !important;
    transform: none !important;
}

/* Divider */
hr {
    border: none !important;
    border-top: 1px solid var(--border) !important;
    margin: 1rem 0 !important;
}

/* ══════════════════════════════════════════
   MAIN AREA
══════════════════════════════════════════ */
.main-wrap {
    display: flex;
    flex-direction: column;
    height: 100vh;
    background: #fff0f5;
    position: relative;
    overflow: hidden;
}

/* Ambient background glow */
.main-wrap::before {
    content: '';
    position: fixed;
    top: -200px; left: 50%;
    transform: translateX(-50%);
    width: 700px; height: 500px;
    background: radial-gradient(ellipse, rgba(108,99,255,0.08) 0%, transparent 70%);
    pointer-events: none;
    z-index: 0;
}

/* Header */
.topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.1rem 2rem;
    border-bottom: 1px solid var(--border);
    background: rgba(7,8,13,0.85);
    backdrop-filter: blur(20px);
    position: sticky; top: 0; z-index: 100;
}
.topbar-title {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 1.1rem;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.topbar-status {
    display: flex;
    align-items: center;
    gap: 7px;
    font-size: 0.75rem;
    color: var(--muted);
}
.status-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    background: var(--accent3);
    box-shadow: 0 0 8px var(--accent3);
    animation: pulse 2s infinite;
}
.status-dot.offline { background: var(--muted); box-shadow: none; animation: none; }
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}

/* Info banner */
.info-banner {
    margin: 1.5rem 2rem 0;
    padding: 0.85rem 1.2rem;
    background: rgba(108,99,255,0.08);
    border: 1px solid rgba(108,99,255,0.2);
    border-radius: 12px;
    font-size: 0.85rem;
    color: #a5b4fc;
    display: flex;
    align-items: center;
    gap: 10px;
}

/* Chat area */
.chat-area {
    flex: 1;
    overflow-y: auto;
    padding: 1.5rem 2rem 2rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
    position: relative;
    z-index: 1;
}

/* Messages */
[data-testid="stChatMessage"] {
    background: #1e2235 !important;
    border: none !important;
    padding: 0 !important;
    margin: 0 !important;
    max-width: 100% !important;
}

/* User messages */
[data-testid="stChatMessage"][data-testid*="user"],
.stChatMessage:has([data-testid="chatAvatarIcon-user"]) {
    background: #1e2235 !important;
    border: 1px solid var(--border) !important;
    border-radius: 16px 16px 4px 16px !important;
    padding: 1rem 1.2rem !important;
    margin-left: 10% !important;
    box-shadow: 0 2px 12px rgba(0,0,0,0.3) !important;
}

/* Assistant messages */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
    background:  #1e2235!important;
    border: 1px solid rgba(108,99,255,0.15) !important;
    border-radius: 16px 16px 16px 4px !important;
    padding: 1rem 1.2rem !important;
    margin-right: 10% !important;
    box-shadow: 0 2px 12px rgba(0,0,0,0.3), 0 0 0 1px rgba(108,99,255,0.05) !important;
}

/* Avatar */
[data-testid="chatAvatarIcon-assistant"],
[data-testid="chatAvatarIcon-user"] {
    background: #1e2235 !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    font-size: 1rem !important;
}

/* Message text */
[data-testid="stChatMessage"] p {
    color: var(--text) !important;
    font-size: 0.9rem !important;
    line-height: 1.7 !important;
}
[data-testid="stChatMessage"] strong {
    color: var(--accent3) !important;
    font-weight: 600 !important;
}
[data-testid="stChatMessage"] h3 {
    font-family: 'Syne', sans-serif !important;
    color: var(--text) !important;
    font-size: 1rem !important;
    margin-bottom: 0.5rem !important;
}
[data-testid="stChatMessage"] ul, [data-testid="stChatMessage"] ol {
    padding-left: 1.2rem !important;
    color: var(--text) !important;
}
[data-testid="stChatMessage"] li {
    font-size: 0.88rem !important;
    line-height: 1.65 !important;
    margin-bottom: 0.2rem !important;
}
[data-testid="stChatMessage"] table {
    width: 100% !important;
    border-collapse: collapse !important;
    font-size: 0.82rem !important;
    margin: 0.5rem 0 !important;
}
[data-testid="stChatMessage"] th {
    background: var(--surface) !important;
    color: var(--accent3) !important;
    padding: 0.5rem 0.8rem !important;
    text-align: left !important;
    font-weight: 600 !important;
    border-bottom: 1px solid var(--border) !important;
}
[data-testid="stChatMessage"] td {
    padding: 0.45rem 0.8rem !important;
    border-bottom: 1px solid var(--border) !important;
    color: var(--text) !important;
}

/* Chat input */
[data-testid="stChatInput"] {
    background: #1e2235 !important;
    border-top: 1px solid var(--border) !important;
    padding: 1rem 2rem !important;
    position: sticky !important;
    bottom: 0 !important;
    z-index: 100 !important;
    backdrop-filter: blur(20px) !important;
}
[data-testid="stChatInput"] textarea {
    background: #1e2235 !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
    padding: 0.85rem 1.1rem !important;
    resize: none !important;
    transition: border 0.2s, box-shadow 0.2s !important;
    line-height: 1.5 !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--glow) !important;
    outline: none !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: var(--muted) !important;
}

/* Send button */
[data-testid="stChatInput"] button {
    background: linear-gradient(135deg, var(--accent), var(--accent2)) !important;
    border: none !important;
    border-radius: 10px !important;
    color: white !important;
    transition: transform 0.15s, box-shadow 0.15s !important;
}
[data-testid="stChatInput"] button:hover {
    transform: scale(1.05) !important;
    box-shadow: 0 4px 20px var(--glow) !important;
}

/* Spinner */
[data-testid="stSpinner"] { color: var(--accent) !important; }

/* Error / info messages */
[data-testid="stAlert"] {
    background: var(--surface) !important;
    border-radius: 12px !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    font-size: 0.85rem !important;
}

/* Welcome empty state */
.empty-state {
    text-align: center;
    padding: 3rem 2rem;
    color: var(--muted);
}
.empty-state-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
    display: block;
}
.empty-state h2 {
    font-family: 'Syne', sans-serif;
    font-size: 1.4rem;
    color: var(--text);
    margin-bottom: 0.5rem;
    font-weight: 700;
}
.empty-state p {
    font-size: 0.88rem;
    max-width: 380px;
    margin: 0 auto;
    line-height: 1.6;
}

/* Capability chips */
.chips {
    display: flex;
    gap: 0.5rem;
    justify-content: center;
    flex-wrap: wrap;
    margin-top: 1.2rem;
}
.chip {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 999px;
    padding: 0.35rem 0.85rem;
    font-size: 0.78rem;
    color: var(--muted);
    display: flex;
    align-items: center;
    gap: 5px;
}
.chip span { color: var(--accent3); }
</style>
""", unsafe_allow_html=True)

init_session()

# ── SIDEBAR ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <div class="sidebar-logo-icon">🧠</div>
        <div class="sidebar-logo-text">BizMind</div>
    </div>
    <div class="sidebar-tagline">AI Business Advisor</div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-label">🔑 Groq API Key</div>', unsafe_allow_html=True)
    api_key = st.text_input(
        label="API Key",
        type="password",
        placeholder="gsk_...",
        label_visibility="collapsed",
    )

    st.divider()
    st.markdown('<div class="section-label">📋 Business Profile</div>', unsafe_allow_html=True)

    profile_text = get_profile_summary()
    if "No details" in profile_text:
        st.markdown('<div class="profile-card"><div class="profile-empty">Start chatting to build your profile</div></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="profile-card">{profile_text}</div>', unsafe_allow_html=True)

    st.divider()
    st.markdown('<div class="section-label">⚡ Quick Actions</div>', unsafe_allow_html=True)

    profile  = st.session_state.get("business_profile", {})
    biz_type = profile.get("business_type", "")

    if st.button("📦  Production Plan"):
        st.session_state["quick_prompt"] = format_prompt("production", biz_type)
    if st.button("📣  Marketing Strategy"):
        st.session_state["quick_prompt"] = format_prompt("marketing", biz_type)
    if st.button("💰  Sales Tactics"):
        st.session_state["quick_prompt"] = format_prompt("sales", biz_type)
    if st.button("📅  30-Day Growth Plan"):
        st.session_state["quick_prompt"] = format_prompt("full_plan", biz_type)

    st.divider()
    st.markdown('<div class="section-label">📊 Analytics</div>', unsafe_allow_html=True)
    if st.button("📈  Run Sales Analysis"):
        st.session_state["run_analysis"] = True

    st.divider()
    if st.button("🔄  New Chat", type="secondary"):
        clear_session()
        st.rerun()

# ── AGENT INIT ────────────────────────────────────────────────
agent_ready = False

if api_key and api_key.startswith("gsk_"):
    if st.session_state.get(KEY_AGENT) is None:
        with st.spinner("Initialising BizMind..."):
            try:
                chain, history = build_agent(api_key)
                st.session_state[KEY_AGENT] = {"chain": chain, "history": history}
                if not get_messages():
                    add_message("assistant", get_welcome_message())
            except Exception as e:
                st.error(f"Failed to initialise: {e}")
    agent_ready = st.session_state.get(KEY_AGENT) is not None

# ── TOPBAR ────────────────────────────────────────────────────
st.markdown(f"""
<div class="topbar">
    <div class="topbar-title">🧠 BizMind — AI Business Advisor</div>
    <div class="topbar-status">
        <div class="status-dot {'status-dot' if agent_ready else 'offline'}"></div>
        {'Online · Ready' if agent_ready else 'Enter API key to start'}
    </div>
</div>
""", unsafe_allow_html=True)

# ── NOT CONNECTED STATE ───────────────────────────────────────
if not agent_ready:
    st.markdown("""
    <div style="display:flex; align-items:center; justify-content:center; min-height:70vh;">
        <div class="empty-state">
            <span class="empty-state-icon">🧠</span>
            <h2>Welcome to BizMind</h2>
            <p>Your AI-powered business advisor for production planning, marketing strategy, and sales optimization.</p>
            <div class="chips">
                <div class="chip"><span>🏭</span> Production</div>
                <div class="chip"><span>📣</span> Marketing</div>
                <div class="chip"><span>💰</span> Sales</div>
                <div class="chip"><span>📊</span> Analytics</div>
            </div>
            <p style="margin-top:1.5rem; font-size:0.82rem;">
                👈 Enter your <strong style="color:#a5b4fc;">Groq API key</strong> in the sidebar to begin.
                <br>Get one free at <strong style="color:#a5b4fc;">console.groq.com</strong>
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── SALES ANALYSIS ────────────────────────────────────────────
if st.session_state.get("run_analysis"):
    st.session_state["run_analysis"] = False
    biz    = st.session_state.get("business_profile", {}).get("business_type", "")
    report = analyse_sales(biz if biz else None)
    add_message("assistant", report)

# ── CHAT HISTORY ──────────────────────────────────────────────
for msg in get_messages():
    role    = msg["role"]
    content = msg["content"]
    avatar  = "🧠" if role == "assistant" else "👤"
    with st.chat_message(role, avatar=avatar):
        st.markdown(content)

# ── QUICK PROMPT ──────────────────────────────────────────────
pending = st.session_state.pop("quick_prompt", None)

# ── CHAT INPUT ────────────────────────────────────────────────
user_input = st.chat_input("Ask BizMind anything about your business…")

if pending:
    user_input = pending

if user_input:
    add_message("user", user_input)
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    context_updates = extract_context(user_input)
    if context_updates:
        update_profile(context_updates)

    agent_data = st.session_state[KEY_AGENT]
    chain      = agent_data["chain"]
    history    = agent_data["history"]

    with st.chat_message("assistant", avatar="🧠"):
        with st.spinner("Thinking…"):
            try:
                response = chain.invoke({
                    "input": user_input,
                    "history": history,
                })

                history.append(HumanMessage(content=user_input))
                history.append(AIMessage(content=response))
                st.session_state[KEY_AGENT]["history"] = history

                add_message("assistant", response)
                st.markdown(response)

            except Exception as e:
                st.error(f"⚠️ {e}")
                st.stop()

    st.rerun()