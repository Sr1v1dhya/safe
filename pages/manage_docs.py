import streamlit as st
import time
from document_processor import process_document
from vector_store import (
    get_document_sources,
    delete_document,
    add_documents,
    clear_collection,
    list_collections,
    create_collection,
    get_default_collection_name,
    set_default_collection,
    delete_collection,
)


def main():
    """Knowledge Base Management Page"""
    st.set_page_config(
        page_title="Knowledge Base Management",
        page_icon="📚",
        layout="wide",
    )

    # Initialize session state variables
    if "upload_complete" not in st.session_state:
        st.session_state.upload_complete = False
    if "upload_message" not in st.session_state:
        st.session_state.upload_message = ""
    if "upload_status" not in st.session_state:
        st.session_state.upload_status = ""
    if "processing" not in st.session_state:
        st.session_state.processing = False

    st.title("📚 Knowledge Base Management")
    st.markdown(
        """
    This page allows you to manage your knowledge base documents.
    Upload new documents, view existing ones, or remove documents that are no longer needed.
    """
    )

    # Create three columns for the page layout
    col1, col2, col3 = st.columns([1, 2, 1])

    # Collection management in column 3
    with col3:
        st.header("Collections")

        # Get current collections
        collections = list_collections()
        collection_names = [c.name for c in collections] if collections else []
        default_collection = get_default_collection_name()

        st.markdown(f"**Current Collection:** {default_collection}")

        # Create new collection
        with st.expander("Create New Collection"):
            new_collection_name = st.text_input(
                "New Collection Name:", key="new_collection_name"
            )
            if st.button("Create Collection", key="create_collection"):
                if new_collection_name and new_collection_name not in collection_names:
                    with st.spinner(f"Creating collection '{new_collection_name}'..."):
                        collection = create_collection(new_collection_name)
                        if collection:
                            st.success(f"Created collection: {new_collection_name}")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error("Failed to create collection")
                elif new_collection_name in collection_names:
                    st.error(f"Collection '{new_collection_name}' already exists")
                else:
                    st.error("Please enter a collection name")

        # Select and manage collections
        if collection_names:
            st.subheader("Available Collections")
            for collection_name in collection_names:
                with st.container(border=True):
                    col_name, col_actions = st.columns([2, 1])

                    with col_name:
                        # Show collection name with indicator if it's default
                        if collection_name == default_collection:
                            st.markdown(f"**{collection_name}** (active)")
                        else:
                            st.markdown(collection_name)

                    with col_actions:
                        # Use button to set as default
                        if collection_name != default_collection:
                            if st.button(
                                "Set Default", key=f"default_{collection_name}"
                            ):
                                set_default_collection(collection_name)
                                st.success(
                                    f"Set {collection_name} as default collection"
                                )
                                time.sleep(0.5)
                                st.rerun()

                        # Delete collection button (if not default)
                        if collection_name != default_collection:
                            if st.button(
                                "Delete",
                                key=f"delete_{collection_name}",
                                type="primary",
                            ):
                                confirmation = st.text_input(
                                    f"Type '{collection_name}' to confirm deletion:",
                                    key=f"confirm_{collection_name}",
                                )
                                if confirmation == collection_name:
                                    if delete_collection(collection_name):
                                        st.success(
                                            f"Deleted collection {collection_name}"
                                        )
                                        time.sleep(0.5)
                                        st.rerun()
                                    else:
                                        st.error(
                                            f"Failed to delete collection {collection_name}"
                                        )

    # Upload section in column 1
    with col1:
        st.header("Upload Documents")

        # Display active collection
        current_collection = get_default_collection_name()
        if current_collection:
            st.info(f"Adding documents to collection: **{current_collection}**")
        else:
            st.warning("No collection selected. Please create or select a collection.")

        # Handle processing state
        if st.session_state.processing:
            with st.spinner("Processing document..."):
                file = st.session_state.file_to_process
                documents = process_document(file, {"source": file.name})
                
                if documents:
                    count = add_documents(documents)
                    st.session_state.upload_complete = True
                    st.session_state.upload_message = f"Added {count} chunks from {file.name} to knowledge base"
                    st.session_state.upload_status = "success"
                else:
                    st.session_state.upload_complete = True
                    st.session_state.upload_message = "Failed to process document. Check the file format."
                    st.session_state.upload_status = "error"
                
                # Reset processing flag
                st.session_state.processing = False
                st.session_state.file_to_process = None
                st.rerun()

        # Display status message from previous uploads if any
        if st.session_state.upload_complete:
            if st.session_state.upload_status == "success":
                st.success(st.session_state.upload_message)
            elif st.session_state.upload_status == "error":
                st.error(st.session_state.upload_message)

        # File uploader
        uploaded_file = st.file_uploader(
            "Upload a document to add to your knowledge base",
            type=["pdf", "txt"],
            help="Upload PDFs or text files",
            key="uploaded_file",
        )

        # Process button
        if uploaded_file:
            if st.button("Process Document", type="primary"):
                st.session_state.file_to_process = uploaded_file
                st.session_state.processing = True
                st.rerun()

        st.divider()

        # Dangerous operations section
        st.header("Maintenance")
        with st.expander("Danger Zone"):
            st.warning("The following actions cannot be undone!")
            st.markdown(
                f"These actions affect the **{get_default_collection_name()}** collection."
            )
            if st.button(
                "Clear Current Collection", type="primary", use_container_width=True
            ):
                confirm = st.text_input(
                    "Type 'DELETE' to confirm clearing the entire collection:"
                )
                if confirm == "DELETE":
                    with st.spinner("Clearing knowledge base..."):
                        if clear_collection():
                            st.success(
                                f"Collection {get_default_collection_name()} cleared successfully"
                            )
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Failed to clear knowledge base")

    # Document list in column 2
    with col2:
        default_collection_name = get_default_collection_name()
        if default_collection_name:
            st.header(f"Documents in {get_default_collection_name()}")

            # Get document sources
            sources = get_document_sources()

            if not sources:
                st.info(
                    f"No documents in the '{get_default_collection_name()}' collection. Upload documents to get started."
                )
            else:
                # Display documents in a table
                st.markdown(f"**Total Documents:** {len(sources)}")

                # Create a table for documents
                data = []
                for source, info in sources.items():
                    data.append(
                        {
                            "Document": source,
                            "Chunks": info["chunks"],
                            "Actions": source,  # We'll use this for button identification
                        }
                    )

                # Display each document as a card
                for doc in data:
                    with st.container(border=True):
                        col_info, col_action = st.columns([3, 1])

                        with col_info:
                            st.subheader(doc["Document"])
                            st.text(f"Chunks: {doc['Chunks']}")

                        with col_action:
                            st.write("")  # Spacing
                            if st.button(
                                "🗑️ Delete", key=f"del_{doc['Actions']}", type="primary"
                            ):
                                with st.spinner(f"Deleting {doc['Document']}..."):
                                    deleted = delete_document(doc["Actions"])
                                    if deleted > 0:
                                        st.success(
                                            f"Deleted {deleted} chunks from {doc['Document']}"
                                        )
                                        time.sleep(1)
                                        st.rerun()
                                    else:
                                        st.error(f"Failed to delete {doc['Document']}")
        else:
            st.warning(
                "No default collection set. Please create or select a collection to manage documents."
            )


if __name__ == "__main__":
    main()