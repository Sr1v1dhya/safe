import streamlit as st
import io
import requests
from PIL import Image
from gemini import (
    get_response,
    initialize_gen_ai_client,
    create_chat,
    get_image_descrption,
)
from session_state import (
    initialise_session_state,
    disable_chat_input,
    set_active_chat,
    new_chat,
)
from chat_db import (
    get_chat_sessions,
    get_messages,
    save_message,
    save_gemini_history,
    update_chat_title,
    get_gemini_history,
    create_new_chat,
    delete_chat_session,
    delete_all_chat_sessions,
)
from vector_store import (
    add_documents,
    query_collection,
    get_all_documents,
    get_default_collection_name,
)
from document_processor import process_document
from rag import generate_prompt_with_context

# Language configuration
LANGUAGES = {
    "en": "English",
    "ta": "Tamil",
    "hi": "Hindi",
    "te": "Telugu"
}

# UI translations for chat bot
UI_TRANSLATIONS = {
    "ta": {
        "page_title": "S.A.F.E. சாட்",
        "sidebar_title": "சாட் வரலாறு",
        "new_chat_button": "➕ புதிய சாட்",
        "delete_all_button": "🗑️ அனைத்து சாட்களையும் அழி",
        "delete_confirm": "அனைத்து சாட்களையும் அழிக்க விரும்புகிறீர்களா? உறுதிப்படுத்த மீண்டும் கிளிக் செய்யவும்.",
        "welcome_title": "### 👋 S.A.F.E. சாட்க்கு வரவேற்கிறோம்!",
        "welcome_message1": "புதிய உரையாடலைத் தொடங்க கீழே ஒரு செய்தியை அனுப்பவும்.",
        "welcome_message2": "பதில்களை மேம்படுத்த அறிவுத் தளப் பக்கத்தில் ஆவணங்களைப் பதிவேற்றவும்.",
        "welcome_message3": "சாட் உள்ளீட்டில் உள்ள இணைப்பு பொத்தானைப் பயன்படுத்தி படங்கள் அல்லது ஒலிக் கோப்புகளையும் பதிவேற்றலாம்.",
        "chat_input": "எதையும் கேளுங்கள்...",
        "transcribing": "ஒலியை எழுத்தாக்குகிறது...",
        "transcription_error": "ஒலி எழுத்தாக்கத்தில் பிழை: {0}",
        "transcribed_audio": "எழுத்தாக்கப்பட்ட ஒலி: {0}",
        "analyze_image": "இந்தப் படத்தை ஆராயுங்கள்.",
        "searching": "அறிவுத் தளத்தைத் தேடுகிறது & பதிலை உருவாக்குகிறது...",
        "delete_chat": "{0} சாட்யை அழி",
        "deleted_chat": "சாட் அழிக்கப்பட்டது: {0}",
        "all_chats_deleted": "அனைத்து சாட்களும் அழிக்கப்பட்டன",
        "language": "மொழி"
    },
    "hi": {
        "page_title": "S.A.F.E. चैटबॉट",
        "sidebar_title": "चैट इतिहास",
        "new_chat_button": "➕ नई चैट",
        "delete_all_button": "🗑️ सभी चैट हटाएं",
        "delete_confirm": "क्या आप सभी चैट हटाना चाहते हैं? पुष्टि करने के लिए फिर से क्लिक करें।",
        "welcome_title": "### 👋 S.A.F.E. चैटबॉट में आपका स्वागत है!",
        "welcome_message1": "नया वार्तालाप शुरू करने के लिए नीचे एक संदेश भेजें।",
        "welcome_message2": "उत्तरों को बेहतर बनाने के लिए नॉलेज बेस पेज पर दस्तावेज अपलोड करें।",
        "welcome_message3": "चैट इनपुट में अटैचमेंट बटन का उपयोग करके छवियां या ऑडियो फ़ाइलें भी अपलोड कर सकते हैं।",
        "chat_input": "कुछ भी पूछें...",
        "transcribing": "ऑडियो को ट्रांसक्राइब कर रहा है...",
        "transcription_error": "ऑडियो ट्रांसक्रिप्शन में त्रुटि: {0}",
        "transcribed_audio": "ट्रांसक्राइब किया गया ऑडियो: {0}",
        "analyze_image": "कृपया इस छवि का विश्लेषण करें।",
        "searching": "नॉलेज बेस खोज रहा है और उत्तर तैयार कर रहा है...",
        "delete_chat": "'{0}' चैट हटाएं",
        "deleted_chat": "चैट हटा दी गई: {0}",
        "all_chats_deleted": "सभी चैट हटा दी गईं",
        "language": "भाषा"
    },
    "te": {
        "page_title": "S.A.F.E. చాట్‌బాట్",
        "sidebar_title": "చాట్ చరిత్ర",
        "new_chat_button": "➕ కొత్త చాట్",
        "delete_all_button": "🗑️ అన్ని చాట్‌లను తొలగించండి",
        "delete_confirm": "మీరు నిజంగా అన్ని చాట్‌లను తొలగించాలనుకుంటున్నారా? నిర్ధారించడానికి మళ్లీ క్లిక్ చేయండి.",
        "welcome_title": "### 👋 S.A.F.E. చాట్‌బాట్‌కి స్వాగతం!",
        "welcome_message1": "కొత్త సంభాషణను ప్రారంభించడానికి క్రింద ఒక సందేశాన్ని పంపండి.",
        "welcome_message2": "సమాధానాలను మెరుగుపరచడానికి నాలెడ్జ్ బేస్ పేజీలో పత్రాలను అప్‌లోడ్ చేయండి.",
        "welcome_message3": "చాట్ ఇన్‌పుట్‌లోని అటాచ్‌మెంట్ బటన్ ఉపయోగించి చిత్రాలు లేదా ఆడియో ఫైల్‌లను కూడా అప్‌లోడ్ చేయవచ్చు.",
        "chat_input": "ఏదైనా అడగండి...",
        "transcribing": "ఆడియోని వ్రాతగా మార్చుతోంది...",
        "transcription_error": "ఆడియో ట్రాన్స్‌క్రిప్షన్‌లో లోపం: {0}",
        "transcribed_audio": "వ్రాతగా మార్చిన ఆడియో: {0}",
        "analyze_image": "దయచేసి ఈ చిత్రాన్ని విశ్లేషించండి.",
        "searching": "నాలెడ్జ్ బేస్‌ను శోధిస్తోంది & సమాధానాన్ని రూపొందిస్తోంది...",
        "delete_chat": "'{0}' చాట్‌ను తొలగించండి",
        "deleted_chat": "చాట్ తొలగించబడింది: {0}",
        "all_chats_deleted": "అన్ని చాట్‌లు తొలగించబడ్డాయి",
        "language": "భాష"
    },
    "en": {
        "page_title": "S.A.F.E. Chatbot",
        "sidebar_title": "Chat History",
        "new_chat_button": "➕ New Chat",
        "delete_all_button": "🗑️ Delete All Chats",
        "delete_confirm": "Are you sure you want to delete ALL chats? Click again to confirm.",
        "welcome_title": "### 👋 Welcome to S.A.F.E. Chatbot!",
        "welcome_message1": "Send a message below to start a new conversation.",
        "welcome_message2": "Upload documents to the knowledge base in the Knowledge Base page to improve answers.",
        "welcome_message3": "You can also upload images or audio files using the attachment button in the chat input.",
        "chat_input": "Ask me anything...",
        "transcribing": "Transcribing audio...",
        "transcription_error": "Error transcribing audio: {0}",
        "transcribed_audio": "Transcribed audio: {0}",
        "analyze_image": "Please analyze this image.",
        "searching": "Searching knowledge base & generating response...",
        "delete_chat": "Delete '{0}' chat",
        "deleted_chat": "Deleted chat: {0}",
        "all_chats_deleted": "All chats deleted",
        "language": "Language"
    }
}

# Initialize session state for language if not exists
if 'language' not in st.session_state:
    st.session_state.language = 'en'  # Default to English

def transcribe_audio_with_groq(audio_file):
    """Transcribe audio using Groq's Whisper API"""
    API_KEY = st.secrets["groq_api_key"]
    GROQ_ENDPOINT = "https://api.groq.com/openai/v1/audio/transcriptions"
    MODEL_NAME = "whisper-large-v3"
    
    headers = {"Authorization": f"Bearer {API_KEY}"}
    data = {
        "model": MODEL_NAME,
        "response_format": "json"
    }
    
    response = requests.post(GROQ_ENDPOINT, headers=headers, files={"file": audio_file}, data=data)
    
    if response.status_code == 200:
        result = response.json()
        return result["text"]
    else:
        raise Exception(f"Error {response.status_code}: {response.text}")


def main():
    """Main function for the chat bot page"""
    # Get current UI translations
    ui = UI_TRANSLATIONS[st.session_state.language]
    
    st.set_page_config(
        page_title=ui["page_title"],
        page_icon="💬",
        layout="wide",
    )
    st.title(ui["page_title"])

    initialise_session_state()

    # Initialize the GenAI client
    genai_client = initialize_gen_ai_client(api_key=st.secrets["gen_ai_api_key"])

    # Sidebar for chat history
    with st.sidebar:
        # Add the app logo
        st.image("firstaid.png", width=80)
        
        # Add language selector
        st.markdown(f"### 🌐 {ui['language']}")
        
        with st.container(border=True):
            selected_language = st.selectbox(
                "Select your preferred language",
                options=list(LANGUAGES.keys()),
                format_func=lambda x: LANGUAGES[x],
                index=list(LANGUAGES.keys()).index(st.session_state.language),
                key="language_selector"
            )
        
        # Update session state when language changes
        if selected_language != st.session_state.language:
            st.session_state.language = selected_language
            st.rerun()  # Rerun the app to reflect language changes
        
        st.divider()
        
        st.title(ui["sidebar_title"])

        # New chat button
        if st.button(ui["new_chat_button"], use_container_width=True):
            new_chat()
            st.rerun()

        # Display chat history
        chat_sessions = get_chat_sessions()
        for session in chat_sessions:
            session_id = session["id"]
            title = session["title"]

            # Create columns for chat button and delete button
            col1, col2 = st.columns([4, 1])
            
            with col1:
                # Highlight active chat
                if session_id == st.session_state.active_chat_id:
                    button_type = "primary"
                else:
                    button_type = "secondary"

                # Display chat session as a button
                if st.button(
                    f"💬 {title}",
                    key=f"chat_{session_id}",
                    use_container_width=True,
                    type=button_type,
                ):
                    set_active_chat(session_id)
                    st.session_state.messages = get_messages(session_id)
                    st.session_state.chat_title = title
                    st.rerun()
            
            with col2:
                # Delete button for each chat
                if st.button(
                    "🗑️",
                    key=f"delete_{session_id}",
                    help=ui["delete_chat"].format(title),
                ):
                    # Confirm before deleting
                    if st.session_state.get(f"confirm_delete_{session_id}", False):
                        delete_chat_session(session_id)
                        st.success(ui["deleted_chat"].format(title))
                        # If we deleted the active chat, clear the session
                        if session_id == st.session_state.active_chat_id:
                            st.session_state.active_chat_id = None
                            st.session_state.messages = []
                            st.session_state.chat_title = "New Chat"
                        st.rerun()
                    else:
                        st.session_state[f"confirm_delete_{session_id}"] = True
                        st.rerun()

        st.divider()
        
        # Delete All button with confirmation
        if st.button(ui["delete_all_button"], use_container_width=True, type="primary"):
            if st.session_state.get("confirm_delete_all", False):
                delete_all_chat_sessions()
                st.success(ui["all_chats_deleted"])
                st.session_state.active_chat_id = None
                st.session_state.messages = []
                st.session_state.chat_title = "New Chat"
                st.rerun()
            else:
                st.session_state["confirm_delete_all"] = True
                st.rerun()

        # Display confirmation message if needed
        if st.session_state.get("confirm_delete_all", False):
            st.warning(ui["delete_confirm"])

        # Clear any confirmation states if they're no longer relevant
        for session in chat_sessions:
            session_id = session["id"]
            if st.session_state.get(f"confirm_delete_{session_id}", False) and session_id not in [s["id"] for s in chat_sessions]:
                del st.session_state[f"confirm_delete_{session_id}"]

        st.divider()

    # Initialize or retrieve chat from active session
    active_chat_id = st.session_state.active_chat_id

    # Only load messages if there's an active chat
    if active_chat_id:
        session_messages = get_messages(active_chat_id)

        # If there are messages in the database but not in session state, load them
        if session_messages and not st.session_state.messages:
            st.session_state.messages = session_messages

        # Get or create a chat session with the Gemini model
        gemini_history = get_gemini_history(active_chat_id)
        chat = create_chat(genai_client, gemini_history)

        # Display messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                # Display images if they exist in the message
                if "images" in message and message["images"]:
                    for img in message["images"]:
                        st.image(img, caption="Uploaded Image")

        # Auto-update the chat title if it's a new chat with content
        if st.session_state.messages and st.session_state.chat_title == "New Chat":
            first_msg = st.session_state.messages[0]["content"]
            new_title = (first_msg[:24] + "...") if len(first_msg) > 24 else first_msg
            st.session_state.chat_title = new_title
            update_chat_title(active_chat_id, new_title)
    else:
        # Show welcome message when no chat is active
        st.markdown(ui["welcome_title"])
        st.markdown(ui["welcome_message1"])
        st.markdown(ui["welcome_message2"])
        st.markdown(ui["welcome_message3"])

    # Chat input with support for both images and audio files
    if prompt := st.chat_input(
        ui["chat_input"],
        accept_file="multiple",
        file_type=["jpg", "jpeg", "png", "mp3", "wav", "m4a"],
        disabled=st.session_state.processing,
        on_submit=disable_chat_input,
    ):
        uploaded_images = []
        transcribed_text = ""

        # Process uploaded files
        if hasattr(prompt, "files") and prompt.files:
            for file in prompt.files:
                file_type = file.type.split('/')[0]
                
                if file_type == 'image':
                    # Handle image files
                    image = Image.open(file)
                    img_bytes = io.BytesIO()
                    image.save(img_bytes, format=image.format if image.format else "PNG")
                    uploaded_images.append(img_bytes.getvalue())
                
                elif file_type == 'audio':
                    # Handle audio files - transcribe them
                    with st.spinner(ui["transcribing"]):
                        try:
                            audio_text = transcribe_audio_with_groq(file)
                            if transcribed_text:
                                transcribed_text += "\n\n" + audio_text
                            else:
                                transcribed_text = audio_text
                        except Exception as e:
                            st.error(ui["transcription_error"].format(str(e)))

        # Add user message to chat history with images
        user_content = prompt.text if hasattr(prompt, "text") else ""
        
        # Add transcribed text to user message if available
        if transcribed_text:
            if user_content:
                user_content += f"\n\n{ui['transcribed_audio'].format(transcribed_text)}"
            else:
                user_content = ui["transcribed_audio"].format(transcribed_text)

        # Create a new chat if none is active
        if not st.session_state.active_chat_id:
            st.session_state.active_chat_id = create_new_chat()
            chat = create_chat(genai_client)

        # Save to database
        save_message(
            st.session_state.active_chat_id, "user", user_content, uploaded_images
        )

        # Update session state
        st.session_state.messages.append(
            {"role": "user", "content": user_content, "images": uploaded_images}
        )

        # Display user message
        with st.chat_message("user"):
            if user_content:
                st.markdown(user_content)
            if uploaded_images:
                for img in uploaded_images:
                    st.image(img, caption="Uploaded Image")

        # Get AI response with RAG
        with st.spinner(ui["searching"]):
            current_collection = get_default_collection_name()

            if user_content and current_collection:
                user_query = user_content
                if hasattr(prompt, "files") and prompt.files:
                    image_files = [f for f in prompt.files if f.type.split('/')[0] == 'image']
                    if image_files:
                        image_descriptions = get_image_descrption(image_files)
                        user_query += "\n" + image_descriptions

                query_results = query_collection(user_query, n_results=100)
                enhanced_prompt = generate_prompt_with_context(user_query, query_results)

                class EnhancedPrompt:
                    def __init__(self, text, files=None):
                        self.text = text
                        self.files = files

                image_files = [f for f in prompt.files if f.type.split('/')[0] == 'image'] if hasattr(prompt, "files") else None
                rag_prompt = EnhancedPrompt(enhanced_prompt, image_files)
                ai_response, gemini_history = get_response(chat, rag_prompt)
            else:
                if hasattr(prompt, "files") and prompt.files:
                    class FilteredPrompt:
                        def __init__(self, text, files=None):
                            self.text = text
                            self.files = files
                    
                    image_files = [f for f in prompt.files if f.type.split('/')[0] == 'image']
                    text_content = prompt.text if hasattr(prompt, "text") and prompt.text else ""
                    
                    if transcribed_text and not text_content:
                        text_content = ui["transcribed_audio"].format(transcribed_text)
                    elif transcribed_text:
                        if ui["transcribed_audio"].format("").strip() not in text_content:
                            text_content += f"\n\n{ui['transcribed_audio'].format(transcribed_text)}"
                    
                    if not text_content and image_files:
                        text_content = ui["analyze_image"]
                        
                    filtered_prompt = FilteredPrompt(text_content, image_files)
                    ai_response, gemini_history = get_response(chat, filtered_prompt)
                else:
                    if not user_content:
                        user_content = "Hello"
                    ai_response, gemini_history = get_response(chat, prompt)

        # Save Gemini history to database
        save_gemini_history(st.session_state.active_chat_id, gemini_history)

        # Save AI response to database
        save_message(st.session_state.active_chat_id, "assistant", ai_response)

        # Display AI response
        with st.chat_message("assistant"):
            st.markdown(ai_response)

        # Add AI response to chat history
        st.session_state.messages.append({"role": "assistant", "content": ai_response})

        # Update the chat title if it's a new chat
        if st.session_state.chat_title == "New Chat":
            first_msg = user_content
            new_title = (first_msg[:24] + "...") if len(first_msg) > 24 else first_msg
            st.session_state.chat_title = new_title
            update_chat_title(st.session_state.active_chat_id, new_title)

        # Re-enable chat input
        st.session_state.processing = False
        st.rerun()

if __name__ == "__main__":
    main()