import streamlit as st
from vector_store import query_collection


def main():
    """Document search page"""
    st.set_page_config(
        page_title="Search Knowledge Base",
        page_icon="🔍",
        layout="wide",
    )
    
    st.title("🔍 Search Knowledge Base")
    st.markdown("""
    Search through your knowledge base to see what information is available.
    This helps you understand what documents the AI can access when answering questions.
    """)
    
    # Search input
    query = st.text_input("Enter a search term:", placeholder="Enter keywords to search your documents")
    col1, col2 = st.columns([1, 3])
    
    with col1:
        num_results = st.slider("Number of results:", min_value=1, max_value=20, value=5)
    
    with col2:
        search_button = st.button("Search", type="primary", use_container_width=True)
    
    # Perform search when button is clicked
    if search_button and query:
        with st.spinner("Searching..."):
            results = query_collection(query, n_results=num_results)
            
            if results and results["documents"] and results["documents"][0]:
                st.success(f"Found {len(results['documents'][0])} relevant passages")
                
                # Display search results
                for i, (doc, metadata, distance) in enumerate(zip(
                    results["documents"][0], 
                    results["metadatas"][0],
                    results["distances"][0]
                )):
                    relevance = (1 - distance) * 100  # Convert distance to relevance percentage
                    
                    with st.expander(f"{i+1}. {metadata.get('source', 'Unknown')} (Relevance: {relevance:.1f}%)"):
                        st.markdown("#### Document Context")
                        st.markdown(doc)
                        st.divider()
                        st.markdown("#### Metadata")
                        st.json(metadata)
            else:
                st.info("No results found. Try a different search term.")
    
    if not query:
        st.info("Enter a search term to find relevant information in your knowledge base.")


if __name__ == "__main__":
    main()