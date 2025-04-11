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
        initial_sidebar_state="expanded"
    )

    # Custom CSS for enhanced dark mode UI
    st.markdown("""
    <style>
    /* Dark mode theme */
    .stApp {
        background-color: #0e1117;
        color: #f9f9fa;
    }
    
    .main-header {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        color: #f9f9fa;
    }
    
    .sub-header {
        font-size: 1.5rem;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
        color: #f9f9fa;
    }
    
    .document-card {
        background-color: #1e2030;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        border: 1px solid #2e3144;
    }
    
    .success-badge {
        background-color: #0f3a2d;
        color: #7eebc3;
        padding: 0.2rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.75rem;
    }
    
    .active-badge {
        background-color: #1e3a5f;
        color: #7eb3eb;
        padding: 0.2rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.75rem;
    }
    
    .collection-name {
        font-weight: bold;
        font-size: 1.1rem;
        color: #f9f9fa;
    }
    
    .upload-section {
        background-color: #1e2030;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border: 1px solid #2e3144;
    }
    
    /* Custom containers */
    .stat-container {
        background-color: #1e2030;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #2e3144;
        margin-bottom: 15px;
    }
    
    .stat-label {
        font-size: 0.8rem;
        color: #8b95a5;
    }
    
    .stat-value {
        font-size: 1.5rem;
        font-weight: bold;
        color: #f9f9fa;
    }
    
    /* Button styles */
    .stButton button {
        border-radius: 6px;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    /* File uploader */
    .uploadedFile {
        background-color: #1e2030 !important;
        border: 1px solid #2e3144 !important;
        border-radius: 8px !important;
    }
    
    /* Container styling */
    [data-testid="stExpander"] {
        background-color: #1e2030;
        border: 1px solid #2e3144;
        border-radius: 8px;
    }
    
    [data-testid="stVerticalBlock"] {
        gap: 0.75rem;
    }
    
    /* Document stats */
    .doc-stat {
        background-color: #232539;
        padding: 5px 10px;
        border-radius: 5px;
        display: inline-block;
        margin-right: 10px;
    }
    
    .doc-stat-label {
        font-size: 0.7rem;
        color: #8b95a5;
    }
    
    .doc-stat-value {
        font-weight: bold;
        color: #f9f9fa;
    }
    
    /* Document icons */
    .doc-icon {
        display: inline-block;
        width: 30px;
        height: 30px;
        line-height: 30px;
        text-align: center;
        background-color: #2a2d4a;
        border-radius: 6px;
        margin-right: 10px;
    }
    
    /* Input fields */
    .stTextInput input {
        background-color: #171923;
        border: 1px solid #2e3144;
        color: #f9f9fa;
        border-radius: 6px;
    }
    
    .stTextInput input:focus {
        border: 1px solid #6b7aff;
        box-shadow: 0 0 0 2px rgba(107, 122, 255, 0.2);
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background-color: #6b7aff;
    }
    
    /* Horizontal divider */
    hr {
        border-color: #2e3144;
    }
    </style>
    """, unsafe_allow_html=True)

    # Initialize session state variables
    if "upload_complete" not in st.session_state:
        st.session_state.upload_complete = False
    if "upload_message" not in st.session_state:
        st.session_state.upload_message = ""
    if "upload_status" not in st.session_state:
        st.session_state.upload_status = ""
    if "processing" not in st.session_state:
        st.session_state.processing = False
    if "delete_confirmation" not in st.session_state:
        st.session_state.delete_confirmation = {}
    if "show_collection_delete" not in st.session_state:
        st.session_state.show_collection_delete = {}

    st.markdown('<h1 class="main-header">📚 Knowledge Base Management</h1>', unsafe_allow_html=True)
    
    # Add tabs for better organization
    tab1, tab2 = st.tabs(["📄 Documents", "🗂️ Collections"])
    
    with tab1:
        # Create two columns for the document management layout
        col1, col2 = st.columns([1, 2])
        
        # Upload section in column 1
        with col1:
            st.markdown('<h2 class="sub-header">Upload Documents</h2>', unsafe_allow_html=True)
            
            # Display active collection
            current_collection = get_default_collection_name()
            if current_collection:
                st.markdown(f"""
                <div style="background-color: #1e2030; padding: 15px; border-radius: 8px; margin-bottom: 15px; border: 1px solid #2e3144;">
                    <span style="font-weight: bold; color: #8b95a5;">ACTIVE COLLECTION:</span>
                    <span style="font-weight: bold; color: #7eb3eb;"> {current_collection}</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("No collection selected. Please create or select a collection.")

            # File uploader with enhanced UI
            #st.markdown('<div class="upload-section">', unsafe_allow_html=True)
            uploaded_file = st.file_uploader(
                "Select a document to add to your knowledge base",
                type=["pdf", "txt", "docx", "csv"],
                help="Upload PDFs, text files, Word documents or CSV files",
                key="uploaded_file",
            )

            # Process button with improved UI
            if uploaded_file:
                file_info_col1, file_info_col2 = st.columns([3, 1])
                with file_info_col1:
                    st.markdown(f"**Selected file:** `{uploaded_file.name}`")
                    file_size = round(uploaded_file.size / 1024, 2)
                    size_unit = "KB"
                    if file_size > 1024:
                        file_size = round(file_size / 1024, 2)
                        size_unit = "MB"
                    st.markdown(f"**Size:** `{file_size} {size_unit}`")
                
                with file_info_col2:
                    process_button = st.button("Process", type="primary", use_container_width=True)
                    if process_button:
                        st.session_state.file_to_process = uploaded_file
                        st.session_state.processing = True
                        st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Handle processing state
            if st.session_state.processing:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i in range(100):
                    progress_bar.progress(i + 1)
                    status_update = "Extracting text..." if i < 30 else "Processing content..." if i < 70 else "Adding to knowledge base..."
                    status_text.text(status_update)
                    time.sleep(0.01)
                
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

            st.divider()
            
            # Maintenance section with improved UI
            st.markdown('<h2 class="sub-header">Maintenance</h2>', unsafe_allow_html=True)
            
            with st.expander("Danger Zone ⚠️"):
                st.warning("The following actions cannot be undone!")
                st.markdown(
                    f"These actions affect the **{get_default_collection_name()}** collection."
                )
                
                if "confirm_clear" not in st.session_state:
                    st.session_state.confirm_clear = False
                
                if not st.session_state.confirm_clear:
                    if st.button("Clear Current Collection", type="primary", use_container_width=True):
                        st.session_state.confirm_clear = True
                        st.rerun()
                else:
                    st.error("⚠️ This will permanently delete all documents in this collection")
                    confirm = st.text_input("Type 'DELETE' to confirm clearing the entire collection:")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Cancel", use_container_width=True):
                            st.session_state.confirm_clear = False
                            st.rerun()
                    with col2:
                        if st.button("Confirm Delete", type="primary", use_container_width=True):
                            if confirm == "DELETE":
                                with st.spinner("Clearing knowledge base..."):
                                    if clear_collection():
                                        st.success(f"Collection {get_default_collection_name()} cleared successfully")
                                        st.session_state.confirm_clear = False
                                        time.sleep(1)
                                        st.rerun()
                                    else:
                                        st.error("Failed to clear knowledge base")
                            else:
                                st.error("Please type 'DELETE' to confirm")

        # Document list in column 2
        with col2:
            default_collection_name = get_default_collection_name()
            if default_collection_name:
                st.markdown(f'<h2 class="sub-header">Documents in {default_collection_name}</h2>', unsafe_allow_html=True)

                # Get document sources
                sources = get_document_sources()

                if not sources:
                    st.info(
                        f"No documents in the '{default_collection_name}' collection. Upload documents to get started."
                    )
                else:
                    # Display statistics
                    total_chunks = sum(info["chunks"] for info in sources.values())
                    st.markdown(f"""
                    <div style="display: flex; gap: 15px; margin-bottom: 15px;">
                        <div class="stat-container" style="flex: 1;">
                            <div class="stat-label">TOTAL DOCUMENTS</div>
                            <div class="stat-value">{len(sources)}</div>
                        </div>
                        <div class="stat-container" style="flex: 1;">
                            <div class="stat-label">TOTAL CHUNKS</div>
                            <div class="stat-value">{total_chunks}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Search and filter
                    st.text_input("Search documents:", key="doc_search", 
                                  placeholder="Type to filter documents...")
                    search_term = st.session_state.doc_search.lower() if hasattr(st.session_state, 'doc_search') else ""
                    
                    # Filter documents based on search term
                    filtered_sources = {
                        source: info for source, info in sources.items() 
                        if search_term in source.lower()
                    }
                    
                    if not filtered_sources and search_term:
                        st.info(f"No documents matching '{search_term}'")
                    
                    # Display documents as cards with improved UI
                    for source, info in filtered_sources.items():
                        with st.container(border=True):
                            doc_col1, doc_col2 = st.columns([4, 1])
                            
                            with doc_col1:
                                # Document type icon based on extension
                                icon = "📄"
                                if source.lower().endswith('.pdf'):
                                    icon = "📕"
                                elif source.lower().endswith('.txt'):
                                    icon = "📝"
                                elif source.lower().endswith('.docx'):
                                    icon = "📘"
                                elif source.lower().endswith('.csv'):
                                    icon = "📊"
                                
                                st.markdown(f"""
                                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                                    <div class="doc-icon">{icon}</div>
                                    <span style="font-size: 1.1rem; font-weight: bold;">{source}</span>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                st.markdown(f"""
                                <div style="display: flex; gap: 10px; margin-top: 5px;">
                                    <div class="doc-stat">
                                        <span class="doc-stat-label">CHUNKS</span>
                                        <span class="doc-stat-value"> {info['chunks']}</span>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            with doc_col2:
                                if f"delete_{source}" not in st.session_state.delete_confirmation:
                                    st.session_state.delete_confirmation[f"delete_{source}"] = False
                                
                                if not st.session_state.delete_confirmation[f"delete_{source}"]:
                                    if st.button("🗑️ Delete", key=f"del_btn_{source}", type="primary", use_container_width=True):
                                        st.session_state.delete_confirmation[f"delete_{source}"] = True
                                        st.rerun()
                                else:
                                    if st.button("Cancel", key=f"cancel_{source}", use_container_width=True):
                                        st.session_state.delete_confirmation[f"delete_{source}"] = False
                                        st.rerun()
                                    if st.button("Confirm", key=f"confirm_{source}", type="primary", use_container_width=True):
                                        with st.spinner(f"Deleting {source}..."):
                                            deleted = delete_document(source)
                                            if deleted > 0:
                                                st.success(f"Deleted {deleted} chunks from {source}")
                                                st.session_state.delete_confirmation[f"delete_{source}"] = False
                                                time.sleep(1)
                                                st.rerun()
                                            else:
                                                st.error(f"Failed to delete {source}")
            else:
                st.warning(
                    "No default collection set. Please create or select a collection in the Collections tab."
                )

    # Collection management tab
    with tab2:
        st.markdown('<h2 class="sub-header">Manage Collections</h2>', unsafe_allow_html=True)

        # Create two columns for the collections layout
        col1, col2 = st.columns([1, 2])
        
        # Create new collection
        with col1:
            #st.markdown('<div style="background-color: #1e2030; padding: 20px; border-radius: 10px; border: 1px solid #2e3144;">', unsafe_allow_html=True)
            st.markdown("### Create New Collection")
            new_collection_name = st.text_input(
                "Collection Name:", key="new_collection_name", 
                placeholder="Enter collection name..."
            )
            create_button = st.button("Create Collection", key="create_collection", type="primary", use_container_width=True)
            
            if create_button:
                # Get current collections
                collections = list_collections()
                collection_names = [c.name for c in collections] if collections else []
                
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
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Collection tips
            with st.expander("Collection Tips"):
                st.markdown("""
                - **Collections** help you organize documents by topic or purpose
                - Create separate collections for different subjects or projects
                - Only one collection can be active at a time
                - Searching will only look within the active collection
                - Use clear, descriptive names for your collections
                """)

        # Show existing collections
        with col2:
            st.markdown("### Available Collections")
            
            # Get current collections
            collections = list_collections()
            collection_names = [c.name for c in collections] if collections else []
            default_collection = get_default_collection_name()
            
            if not collection_names:
                st.info("No collections found. Create your first collection to get started.")
            else:
                # Sort collections - default first, then alphabetically
                sorted_names = sorted(collection_names)
                if default_collection in sorted_names:
                    sorted_names.remove(default_collection)
                    sorted_names.insert(0, default_collection)
                
                # Filter collections
                st.text_input("Search collections:", key="collection_search", 
                              placeholder="Type to filter collections...")
                search_term = st.session_state.collection_search.lower() if hasattr(st.session_state, 'collection_search') else ""
                
                filtered_collections = [name for name in sorted_names if search_term in name.lower()]
                
                if not filtered_collections and search_term:
                    st.info(f"No collections matching '{search_term}'")
                
                # Display collections with enhanced UI
                for collection_name in filtered_collections:
                    with st.container(border=True):
                        is_default = collection_name == default_collection
                        col_info, col_actions = st.columns([3, 2])
                        
                        with col_info:
                            if is_default:
                                st.markdown(f"""
                                <div class="collection-name">{collection_name} 
                                    <span class="active-badge">ACTIVE</span>
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.markdown(f"""
                                <div class="collection-name">{collection_name}</div>
                                """, unsafe_allow_html=True)
                        
                        with col_actions:
                            if not is_default:
                                if st.button("Set Active", key=f"default_{collection_name}", use_container_width=True):
                                    set_default_collection(collection_name)
                                    st.success(f"Set {collection_name} as active collection")
                                    time.sleep(0.5)
                                    st.rerun()
                                
                                # Delete collection button (if not default)
                                delete_key = f"delete_collection_{collection_name}"
                                if delete_key not in st.session_state.show_collection_delete:
                                    st.session_state.show_collection_delete[delete_key] = False
                                
                                if not st.session_state.show_collection_delete[delete_key]:
                                    if st.button("Delete", key=delete_key, type="primary", use_container_width=True):
                                        st.session_state.show_collection_delete[delete_key] = True
                                        st.rerun()
                                else:
                                    st.error("⚠️ Are you sure? This will delete all documents in this collection.")
                                    confirmation = st.text_input(
                                        f"Type '{collection_name}' to confirm deletion:",
                                        key=f"confirm_{collection_name}"
                                    )
                                    
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        if st.button("Cancel", key=f"cancel_delete_{collection_name}", use_container_width=True):
                                            st.session_state.show_collection_delete[delete_key] = False
                                            st.rerun()
                                    with col2:
                                        if st.button("Delete", key=f"confirm_delete_{collection_name}", type="primary", use_container_width=True):
                                            if confirmation == collection_name:
                                                if delete_collection(collection_name):
                                                    st.success(f"Deleted collection {collection_name}")
                                                    st.session_state.show_collection_delete[delete_key] = False
                                                    time.sleep(0.5)
                                                    st.rerun()
                                                else:
                                                    st.error(f"Failed to delete collection {collection_name}")
                                            else:
                                                st.error("Collection name doesn't match")


if __name__ == "__main__":
    main()