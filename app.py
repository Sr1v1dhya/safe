import streamlit as st

# Set page config (must be the first Streamlit command)
st.set_page_config(
    page_title="Start page",
    page_icon="🏠",
    layout="wide",
)

st.write(
    """
    # Welcome to the S.A.F.E. Chatbot
    This is a demo of the S.A.F.E. Chatbot, an AI-powered chatbot that can answer your questions based on your knowledge base.
    You can upload documents, search through them, and chat with the AI.
    """
)
