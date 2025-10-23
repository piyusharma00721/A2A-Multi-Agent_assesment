import streamlit as st
import os
from pathlib import Path
import tempfile
from orchestrator.graph import graph
from utils.logger import log_step
from utils.vector_store import VectorStoreManager
import logging

logger = logging.getLogger(__name__)

# Session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "recent_chats" not in st.session_state:
    st.session_state.recent_chats = []
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []
if "vector_manager" not in st.session_state:
    st.session_state.vector_manager = VectorStoreManager()

# Custom CSS
st.markdown("""
    <style>
    .chat-input { display: flex; align-items: center; }
    .attach-btn { margin-right: 10px; }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 AI Assistant")
st.caption("Help you with file Q/A and web search.")

# Sidebar
with st.sidebar:
    st.header("📝 Recent Chats")
    for i, chat in enumerate(st.session_state.recent_chats):
        if st.button(f"Chat {i+1}: {chat['user'][:50]}...", key=f"chat_{i}"):
            st.session_state.chat_history = [chat]
            st.rerun()
    st.divider()
    st.header("📁 Files")
    for file_name in list(st.session_state.uploaded_files):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.text(file_name)
        with col2:
            if st.button("❌", key=f"rm_{file_name}"):
                st.session_state.vector_manager.remove_file(file_name)
                st.session_state.uploaded_files.remove(file_name)
                st.rerun()

# Main chat area
for msg in st.session_state.chat_history:
    with st.chat_message("user"):
        st.write(msg["user"])
    with st.chat_message("assistant"):
        st.write(msg["assistant"])

# File uploader
uploaded_file = st.file_uploader("📎 Attach file", type=['pdf', 'txt', 'csv', 'png', 'jpg', 'jpeg'], key="file_uploader")

if uploaded_file is not None and uploaded_file.name not in st.session_state.uploaded_files:
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name
    
    upload_status = st.status("Processing file...")
    
    try:
        with upload_status:
            success = st.session_state.vector_manager.load_and_embed_file(tmp_path, uploaded_file.name)
            if success:
                st.session_state.uploaded_files.append(uploaded_file.name)
                st.success(f"✅ Uploaded and processed: {uploaded_file.name}")
                st.info(f"📊 Status: Check terminal for detailed logs (e.g., # docs extracted).")
            else:
                st.error(f"❌ Partial failure for {uploaded_file.name}—try re-uploading.")
    except ValueError as e:
        st.error(f"❌ Upload failed: {str(e)}")
        st.info("💡 Tip: For PDFs, ensure it's text-selectable (not scanned). Use TXT for testing.")
    finally:
        os.unlink(tmp_path)
    st.rerun()

has_file = bool(uploaded_file) or bool(st.session_state.uploaded_files)

# Input row
col1, col2 = st.columns([4, 1])
with col1:
    query = st.text_input("Ask a question:", key="query_input", placeholder="Type your query...")
with col2:
    send_btn = st.button("Send", type="primary")

if send_btn and query:
    log_step("App.send_btn", f"Processing query: {query}, Has file: {has_file}")
    
    with st.chat_message("user"):
        st.write(query)
        user_msg = query
    
    # Validate file before query
    file_name = uploaded_file.name if uploaded_file else (st.session_state.uploaded_files[-1] if st.session_state.uploaded_files else "")
    manager = st.session_state.vector_manager
    if has_file and file_name not in manager.vector_stores and file_name not in manager.fallback_texts:
        st.error(f"❌ No processed data for '{file_name}'. Re-upload or choose another file.")
        st.rerun()
    
    state = {
        "query": query,
        "has_file": has_file,
        "route": "",
        "agent_output": "",
        "final_response": "",
        "file_name": file_name
    }
    
    with st.spinner("Thinking..."):
        result = graph.invoke(state)
    
    with st.chat_message("assistant"):
        response = result["final_response"]
        st.write(response)
    
    # Update history
    st.session_state.chat_history.append({"user": user_msg, "assistant": response})
    if not any(c["user"] == query for c in st.session_state.recent_chats):
        st.session_state.recent_chats.append({"user": query, "title": query[:50]})
    
    st.rerun()