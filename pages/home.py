import streamlit as st
import io
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
)
from vector_store import (
    add_documents,
    query_collection,
    get_all_documents,
    get_default_collection_name,
)
from document_processor import process_document
from rag import generate_prompt_with_context


def main():
    """Main function for the home page"""
    st.set_page_config(
        page_title="S.A.F.E. Chatbot",
        page_icon="💬",
        layout="wide",
    )
    # Initialise session state and run the app
    st.title("S.A.F.E. Chatbot")

    initialise_session_state()

    # Initialize the GenAI client
    genai_client = initialize_gen_ai_client(api_key=st.secrets["gen_ai_api_key"])

    # Sidebar for chat history
    with st.sidebar:
        st.title("Chat History")

        # New chat button
        if st.button("➕ New Chat", use_container_width=True):
            new_chat()
            st.rerun()

        # Display chat history
        chat_sessions = get_chat_sessions()
        for session in chat_sessions:
            session_id = session["id"]
            title = session["title"]

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

        st.divider()

        # Knowledge base stats
        # with st.expander("Knowledge Base Status"):
        #     try:
        #         all_docs = get_all_documents()
        #         if all_docs and "documents" in all_docs and all_docs["documents"]:
        #             unique_sources = set()
        #             for metadata in all_docs["metadatas"]:
        #                 if "source" in metadata:
        #                     unique_sources.add(metadata["source"])

        #             st.info(
        #                 f"{len(unique_sources)} documents with {len(all_docs['documents'])} total chunks."
        #             )
        #             st.write("For detailed management, go to the Knowledge Base page.")
        #         else:
        #             st.info("Knowledge base is empty.")
        #     except Exception as e:
        #         st.error(f"Error retrieving knowledge base stats: {str(e)}")

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
            # Use the first 24 characters of the first message as the title
            new_title = (first_msg[:24] + "...") if len(first_msg) > 24 else first_msg
            st.session_state.chat_title = new_title
            update_chat_title(active_chat_id, new_title)
    else:
        # Show welcome message when no chat is active
        st.markdown("### 👋 Welcome to S.A.F.E. Chatbot!")
        st.markdown("Send a message below to start a new conversation.")
        st.markdown(
            "Upload documents to the knowledge base in the Knowledge Base page to improve answers."
        )

    # Chat input
    if prompt := st.chat_input(
        "Ask me anything...",
        accept_file="multiple",
        file_type=["jpg", "jpeg", "png"],
        disabled=st.session_state.processing,
        on_submit=disable_chat_input,
    ):
        uploaded_images = []

        # Process uploaded files
        if hasattr(prompt, "files") and prompt.files:
            for file in prompt.files:
                # Read and save images to session state
                image = Image.open(file)
                # Convert to bytes for storage
                img_bytes = io.BytesIO()
                image.save(img_bytes, format=image.format if image.format else "PNG")
                uploaded_images.append(img_bytes.getvalue())

        # Add user message to chat history with images
        user_content = prompt.text if hasattr(prompt, "text") else ""

        # Create a new chat if none is active
        if not st.session_state.active_chat_id:
            st.session_state.active_chat_id = create_new_chat()
            # Initialize the gemini chat without history since it's new
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
        with st.spinner("Searching knowledge base & generating response..."):
            # Query the vector database for relevant documents only if there's a selected collection
            current_collection = get_default_collection_name()

            if (
                user_content and current_collection
            ):  # Only query if there's text content and a selected collection
                user_query = user_content
                if hasattr(prompt, "files") and prompt.files:
                    image_descriptions = get_image_descrption(prompt.files)
                    print("Image descriptions:", image_descriptions)
                    user_query += "\n" + image_descriptions

                query_results = query_collection(user_query, n_results=100)

                # Create a RAG-enhanced prompt
                enhanced_prompt = generate_prompt_with_context(
                    user_query, query_results
                )

                # Create a custom prompt object that mimics the original prompt's interface
                class EnhancedPrompt:
                    def __init__(self, text, files=None):
                        self.text = text
                        self.files = files

                rag_prompt = EnhancedPrompt(
                    enhanced_prompt, prompt.files if hasattr(prompt, "files") else None
                )

                # Get the response using the enhanced prompt
                ai_response, gemini_history = get_response(chat, rag_prompt)
            else:
                # If there's no text content or no collection selected, just pass the original prompt
                ai_response, gemini_history = get_response(chat, prompt)

            print("\n\nChat history:", gemini_history)
            print()

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
            # Use the first 24 characters of the first message as the title
            new_title = (first_msg[:24] + "...") if len(first_msg) > 24 else first_msg
            st.session_state.chat_title = new_title
            update_chat_title(st.session_state.active_chat_id, new_title)

        # Re-enable chat input
        st.session_state.processing = False

        # Rerun the app to update the chat history
        st.rerun()


if __name__ == "__main__":
    main()
