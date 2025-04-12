import streamlit as st
from typing import Dict, Any

# Language support
LANGUAGES = {
    "en": "English",
    "ta": "Tamil",
    "hi": "Hindi",
    "te": "Telugu"
}

# UI translations dictionary - import from your gemini.py or define here
# This should contain all the UI text translations needed across all pages
from gemini import UI_TRANSLATIONS

def initialize_language_state():
    """Initialize language in session state if not already present."""
    if 'language' not in st.session_state:
        st.session_state.language = "en"  # Default to English

def get_current_language():
    """Get the current language from session state."""
    initialize_language_state()
    return st.session_state.language

def set_language(lang_code):
    """Set the language in session state."""
    if lang_code in LANGUAGES:
        st.session_state.language = lang_code

def add_language_selector():
    """Add a language selector to the sidebar and return the selected language."""
    # Make sure language is initialized
    initialize_language_state()
    
    # Use the current language for the UI text
    current_ui = UI_TRANSLATIONS.get(st.session_state.language, UI_TRANSLATIONS["en"])
    
    # Create the language selector
    with st.sidebar:
        selected_language = st.selectbox(
            current_ui["language_selector"],
            options=list(LANGUAGES.keys()),
            format_func=lambda x: LANGUAGES[x],
            index=list(LANGUAGES.keys()).index(st.session_state.language)
        )
        
        # Update session state when language changes
        if selected_language != st.session_state.language:
            set_language(selected_language)
            st.rerun()  # Rerun the app to reflect language changes
    
    return st.session_state.language

def get_ui_text(key=None):
    """
    Get UI text translations for the selected language.
    If key is provided, return only that specific text item.
    """
    lang = get_current_language()
    ui_dict = UI_TRANSLATIONS.get(lang, UI_TRANSLATIONS["en"])
    
    if key is not None:
        return ui_dict.get(key, UI_TRANSLATIONS["en"].get(key, ""))
    
    return ui_dict