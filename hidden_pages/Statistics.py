import streamlit as st
from vector_store import query_collection

def main():
    """Document search page with dark mode UI"""
    st.set_page_config(
        page_title="Search Knowledge Base",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Apply custom CSS for dark mode
    st.markdown("""
    <style>
    /* Complete dark mode styling */
    /* Main background and text */
    .stApp {
        background-color: #121212;
        color: #e0e0e0;
    }
    
    /* Title styling */
    .search-title h1 {
        color: #e0e0e0;
    }
    
    /* All standard text */
    p, h1, h2, h3, h4, h5, h6, li {
        color: #e0e0e0 !important;
    }
    
    /* Input field styling */
    .stTextInput > div > div > input {
        background-color: #2d2d2d;
        color: #e0e0e0;
        border: 1px solid #444;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #7b68ee;
        color: white;
        border: none;
    }
    .stButton > button:hover {
        background-color: #9370db;
        color: white;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #1e1e1e !important;
        color: #e0e0e0 !important;
        border-radius: 4px !important;
        border-left: 2px solid #7b68ee !important;
    }
    div.streamlit-expanderHeader:hover {
        background-color: #2d2d2d !important;
    }
    .streamlit-expanderContent {
        background-color: #1e1e1e !important;
        color: #e0e0e0 !important;
        border-top: none !important;
        border-left: 2px solid #7b68ee !important;
    }
    
    /* Alert/info box styling */
    .stAlert {
        background-color: #1e1e1e !important;
        color: #e0e0e0 !important;
    }
    .stAlert > div > div > div > div > div:first-child {
        background-color: #7b68ee !important;
    }

    /* Slider styling */
    .stSlider > div > div {
        background-color: #333333;
    }
    .stSlider > div > div > div > div {
        background-color: #7b68ee;
    }
    
    /* Metadata styling */
    pre {
        background-color: #2d2d2d !important;
        color: #e0e0e0 !important;
    }
    code {
        background-color: #2d2d2d !important;
        color: #e0e0e0 !important;
    }
    
    /* Tips card styling */
    .tips-card {
        background-color: #1e1e1e;
        border-radius: 4px;
        padding: 15px;
        height: 100%;
        border-left: 2px solid #7b68ee;
    }
    
    /* Spinner */
    .stSpinner > div > div {
        border-top-color: #7b68ee !important;
    }
    
    /* Relevance bar */
    .relevance-bar {
        height: 4px;
        background: #333333;
        margin-bottom: 15px;
    }
    .relevance-fill {
        height: 100%;
        background-color: #7b68ee;
    }
    
    /* Success/warning icons */
    .success-icon {
        color: #7b68ee;
    }
    .warning-icon {
        color: #ffa500;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header with icon
    st.markdown('<div class="search-title"><h1>🔍 Search Knowledge Base</h1></div>', unsafe_allow_html=True)
    
    # App description with styling
    st.markdown('<div class="app-description">Search through your knowledge base to see what information is available.</div>', unsafe_allow_html=True)
    
    # Search area
    st.markdown("### Enter your search query")
    query = st.text_input("", placeholder="Enter keywords to search your documents", key="search_input")
    
    col1, col2, col3 = st.columns([1.5, 1, 1.5])
    
    with col1:
        num_results = st.slider("Number of results:", min_value=1, max_value=20, value=5)
    
    with col2:
        min_relevance = st.slider("Min. relevance (%):", min_value=0, max_value=100, value=50)
    
    with col3:
        search_button = st.button("🔎 Search Documents", type="primary", use_container_width=True)
    
    # Show animated loading
    if search_button and query:
        with st.spinner("🔍 Searching knowledge base..."):
            results = query_collection(query, n_results=num_results)
            
            if results and results["documents"] and results["documents"][0]:
                filtered_results = []
                # Process results with relevance filtering
                for i, (doc, metadata, distance) in enumerate(zip(
                    results["documents"][0], 
                    results["metadatas"][0],
                    results["distances"][0]
                )):
                    relevance = (1 - distance) * 100  # Convert distance to relevance percentage
                    if relevance >= min_relevance:
                        filtered_results.append((doc, metadata, relevance))
                
                # Show results count
                if filtered_results:
                    st.markdown(f'<div class="success-icon">✅ Found {len(filtered_results)} relevant passages with {min_relevance}%+ relevance</div>', unsafe_allow_html=True)
                    
                    # Display search results with properly styled expanders
                    for i, (doc, metadata, relevance) in enumerate(filtered_results):
                        source = metadata.get('source', 'Unknown document')
                        
                        # Using streamlit expanders but with custom styling
                        with st.expander(f"📄 {source} (Relevance: {relevance:.1f}%)"):
                            # Simple relevance bar without images
                            st.markdown(f"""
                            <div class="relevance-bar">
                                <div class="relevance-fill" style="width: {relevance}%;"></div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Document content
                            st.markdown("#### Document Content")
                            st.markdown(doc)
                            
                            # Metadata
                            st.markdown("#### Metadata")
                            st.code(str(metadata), language="json")
                else:
                    st.markdown(f'<div class="warning-icon">🔍 Found results, but none met the minimum relevance threshold of {min_relevance}%</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="warning-icon">🤔 No results found. Try different search terms or check your knowledge base.</div>', unsafe_allow_html=True)
    
    if not query:
        # Show tips when no search is active
        st.markdown("### 💡 Search Tips")
        
        # Tips in columns
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="tips-card">
            <h4>Effective Searching:</h4>
            <ul>
                <li>Use specific keywords instead of full sentences</li>
                <li>Try synonyms if you don't find what you need</li>
                <li>Adjust the relevance slider for better results</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="tips-card">
            <h4>Understanding Results:</h4>
            <ul>
                <li>Higher relevance percentage = better match</li>
                <li>Check document source to identify origin</li>
                <li>View metadata for additional context</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()