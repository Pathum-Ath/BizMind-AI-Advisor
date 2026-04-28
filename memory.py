"""
memory.py
─────────────────────────────────────────────────────────────
Manages Streamlit session state:
  - Chat history (list of messages)
  - Business profile (extracted context about the user's business)
  - Agent instance (persisted across reruns)
─────────────────────────────────────────────────────────────
"""

import streamlit as st

# ── Session state keys ──────────────────────────────────────
KEY_CHAT     = "chat_history"       # list of {"role": ..., "content": ...}
KEY_PROFILE  = "business_profile"   # dict of detected business details
KEY_AGENT    = "agent"              # LangChain ConversationChain instance


def init_session():
    """
    Initialise all session_state variables on first app load.
    Call this at the very top of app.py before anything else.
    Streamlit reruns the script on every interaction, so we guard
    each key with 'not in st.session_state'.
    """
    if KEY_CHAT not in st.session_state:
        st.session_state[KEY_CHAT] = []

    if KEY_PROFILE not in st.session_state:
        st.session_state[KEY_PROFILE] = {
            "business_type":    None,
            "target_customers": None,
            "budget":           None,
            "sales_situation":  None,
            "location":         None,
        }

    if KEY_AGENT not in st.session_state:
        st.session_state[KEY_AGENT] = None


def add_message(role: str, content: str):
    """
    Append a message to the chat history.

    Args:
        role    : "user" or "assistant"
        content : The message text
    """
    st.session_state[KEY_CHAT].append({"role": role, "content": content})


def get_messages() -> list:
    """Return the full chat history as a list of dicts."""
    return st.session_state.get(KEY_CHAT, [])


def update_profile(updates: dict):
    """
    Merge new detected fields into the business profile.
    Only overwrites fields that have a non-None value in `updates`.

    Args:
        updates : dict of field → value pairs (from utils.extract_context)
    """
    profile = st.session_state.get(KEY_PROFILE, {})
    for key, value in updates.items():
        if value:  # only store non-empty values
            profile[key] = value
    st.session_state[KEY_PROFILE] = profile


def get_profile() -> dict:
    """Return the current business profile dict."""
    return st.session_state.get(KEY_PROFILE, {})


def get_profile_summary() -> str:
    """
    Build a markdown summary of the known business profile.
    Displayed in the sidebar so the user can see what the agent remembers.
    """
    profile = get_profile()

    labels = {
        "business_type":    "🏪 Business Type",
        "target_customers": "👥 Target Customers",
        "budget":           "💰 Budget",
        "sales_situation":  "📊 Sales Situation",
        "location":         "📍 Location",
    }

    lines = []
    for key, label in labels.items():
        val = profile.get(key)
        if val:
            lines.append(f"**{label}:** {val}")

    if not lines:
        return "_No details captured yet. Start chatting to build your profile!_"

    return "\n\n".join(lines)


def clear_session():
    """
    Reset the entire session — used by the 'New Chat' button.
    Deletes chat history, business profile, and the agent instance.
    """
    for key in [KEY_CHAT, KEY_PROFILE, KEY_AGENT]:
        if key in st.session_state:
            del st.session_state[key]
