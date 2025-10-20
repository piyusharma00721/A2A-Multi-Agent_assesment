#!/usr/bin/env python3
"""
Refactored Streamlit Web UI for Multi-Agent Query Router
- Improved alignment and spacing
- Added popup-style file upload window
- Enhanced response visualization
- Retains typing effect and chat persistence
"""

import streamlit as st
import os
import time
import json
import tempfile
from orchestrator import MultiAgentOrchestrator
from utils.logger import logger
from config import Config

# ---- Page Setup ---- #
st.set_page_config(page_title="AI Assistant", page_icon="🤖", layout="wide")

# ---- Custom CSS ---- #
st.markdown("""
<style>
#MainMenu, footer, header {visibility: hidden;}

.main .block-container {padding: 0; margin: 0; max-width: 100%;}
.chat-container {flex: 1; overflow-y: auto; background: #f8f9fa; padding: 1rem;}
.input-container {background: white; border-top: 1px solid #e9ecef; display: flex; align-items: center; gap: 0.5rem; padding: 1rem; position: sticky; bottom: 0; z-index: 100;}

/* Improved header */
.app-title {text-align: center; font-size: 1.5rem; font-weight: 600; margin: 1rem 0; color: #007bff;}
.subtitle {text-align: center; font-size: 1rem; color: #6c757d; margin-bottom: 1rem;}

/* Popup upload */
.upload-popup {position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; padding: 2rem; border-radius: 10px; box-shadow: 0 4px 20px rgba(0,0,0,0.15); width: 400px; z-index: 999;}
.overlay {position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.4); z-index: 998;}
</style>
""", unsafe_allow_html=True)

# ---- Initialize ---- #
@st.cache_resource
def init_orchestrator():
    try:
        return MultiAgentOrchestrator()
    except Exception as e:
        st.error(f"Failed to init orchestrator: {e}")
        return None

def init_session():
    for key, val in {
        'messages': [], 'chat_history': [], 'file_paths': [], 'uploaded_files': [],
        'current_conversation': None, 'show_upload': False
    }.items():
        if key not in st.session_state:
            st.session_state[key] = val

# ---- Sidebar ---- #
def sidebar():
    with st.sidebar:
        st.title("🤖 AI Assistant")
        status = Config.validate_config()
        if status['valid']:
            st.success("🟢 System Online")
        else:
            st.error("🔴 System Offline")
            for i in status['issues']: st.warning(i)

        if st.button("➕ New Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.file_paths = []
            st.session_state.uploaded_files = []
            st.session_state.current_conversation = None
            st.rerun()

        st.divider()
        st.subheader("💬 Chat History")
        for i, conv in enumerate(st.session_state.chat_history):
            if st.button(conv.get('title', f'Chat {i+1}'), key=f'hist_{i}', use_container_width=True):
                st.session_state.messages = conv.get('messages', [])
                st.session_state.file_paths = conv.get('file_paths', [])
                st.session_state.current_conversation = i
                st.rerun()

        st.divider()
        st.subheader("⚙️ Settings")
        st.selectbox("Model", ["Gemini Pro", "GPT-4", "Claude"], key="model")
        st.slider("Temperature", 0.0, 1.0, 0.7, 0.1, key="temp")
        st.slider("Max Tokens", 100, 4000, 1000, 100, key="max_toks")

# ---- Chat Window ---- #
def render_chat():
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if not st.session_state.messages:
        with st.chat_message("assistant"):
            st.markdown("👋 Hi! I'm your AI assistant. How can I help today?")

# ---- File Upload Popup ---- #
def upload_popup():
    st.markdown('<div class="overlay"></div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="upload-popup">', unsafe_allow_html=True)
        st.markdown("### 📎 Upload Files")
        up = st.file_uploader("Drop files or browse", accept_multiple_files=True)
        if up:
            tmp = tempfile.mkdtemp()
            for f in up:
                p = os.path.join(tmp, f.name)
                with open(p, "wb") as file: file.write(f.getbuffer())
                st.session_state.uploaded_files.append({'name': f.name, 'path': p})
                st.session_state.file_paths.append(p)
            st.success(f"✅ Uploaded {len(up)} file(s)")
        if st.button("Close", use_container_width=True):
            st.session_state.show_upload = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ---- Query Processor ---- #
def handle_query(prompt: str):
    st.session_state.messages.append({"role": "user", "content": prompt})
    orch = init_orchestrator()
    if not orch:
        st.error("System not available")
        return

    with st.spinner("🤔 Thinking..."):
        start = time.time()
        result = orch.process_query(prompt, st.session_state.file_paths)
        t = time.time() - start

        if result.get('error'):
            msg = f"❌ {result['error']}"
        else:
            ans = result.get('final_response', {}).get('answer', 'No response')
            msg = ans

        with st.chat_message("assistant"):
            resp = st.empty(); txt = ""
            for w in msg.split():
                txt += w + " "; resp.markdown(txt); time.sleep(0.03)

        st.session_state.messages.append({"role": "assistant", "content": msg, "metadata": {'time': t}})

# ---- Main ---- #
def main():
    init_session()
    sidebar()

    st.markdown('<div class="app-title">AI Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">LangChain + Gemini + Web Search Orchestration</div>', unsafe_allow_html=True)

    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    render_chat()
    st.markdown('</div>', unsafe_allow_html=True)

    # Input
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([0.1, 0.8, 0.1])
    with c1:
        if st.button("📎", use_container_width=True):
            st.session_state.show_upload = True
            st.rerun()
    with c2:
        query = st.text_input("Type your query...", key="input", label_visibility="collapsed")
    with c3:
        if st.button("➤", use_container_width=True) and query:
            handle_query(query)
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.show_upload:
        upload_popup()

if __name__ == "__main__":
    main()
