import streamlit as st
from chat_db import init_db, create_new_chat


def initialise_session_state():
    """
    Initialise session state variables from streamlit
    """
    # Initialize database on first run
    init_db()
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "processing" not in st.session_state:
        st.session_state.processing = False
    if "uploaded_images" not in st.session_state:
        st.session_state.uploaded_images = []
    if "active_chat_id" not in st.session_state:
        # Set to None instead of creating a new chat
        st.session_state.active_chat_id = None
    if "chat_title" not in st.session_state:
        st.session_state.chat_title = "New Chat"
    if "knowledge_base_docs" not in st.session_state:
        st.session_state.knowledge_base_docs = []
    if "speech_input" not in st.session_state:
        st.session_state.speech_input = ""

def disable_chat_input():
    """
    Disable chat input from streamlit
    """
    st.session_state.processing = True


def set_active_chat(chat_id):
    """
    Set the active chat session
    """
    st.session_state.active_chat_id = chat_id


def new_chat():
    """
    Create a new chat session
    """
    st.session_state.active_chat_id = None  # Set to None instead of creating a new chat
    st.session_state.messages = []
    st.session_state.chat_title = "New Chat"