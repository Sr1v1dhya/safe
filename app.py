import streamlit as st
import importlib.util
import os

# Get URL query params early
params = st.query_params
hidden_page = params.get("page")

# Only call set_page_config here if NOT loading a hidden page
if hidden_page not in ["Data_Upload", "Statistics"]:
    st.set_page_config(page_title="SAFE App", page_icon="🛡", layout="wide")

# Route to hidden pages
if hidden_page in ["Data_Upload", "Statistics"]:
    file_path = f"hidden_pages/{hidden_page}.py"
    if os.path.exists(file_path):
        spec = importlib.util.spec_from_file_location("hidden_module", file_path)
        hidden_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(hidden_module)
        hidden_module.main()  # assumes each hidden page defines main()
    else:
        st.set_page_config(page_title="Error", layout="centered")
        st.error("Page not found")

else:
    # Default homepage UI
    st.title("🏠 Welcome to the S.A.F.E. Chatbot")
    st.markdown("""
        This is a demo of the *S.A.F.E. Chatbot*, an AI-powered assistant that can answer your questions based on your knowledge base.  
        You can upload documents, search through them, and chat with the AI.
    """)