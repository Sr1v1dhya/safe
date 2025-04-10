import os
import chromadb
import streamlit as st
from chromadb.utils import embedding_functions
from typing import List, Dict, Any


@st.cache_resource
def get_chroma_client():
    """Get or create a ChromaDB client."""
    os.makedirs("data/chromadb", exist_ok=True)
    client = chromadb.PersistentClient(path="data/chromadb")
    return client


@st.cache_resource
def get_embedding_function():
    """Get the embedding function."""
    return embedding_functions.GoogleGenerativeAiEmbeddingFunction(
        api_key=st.secrets["gen_ai_api_key"]
    )


def get_default_collection_name():
    """Get the default collection name from session state."""
    if "default_collection" not in st.session_state:
        # list collections
        collections = list_collections()
        if collections:
            # Use the first collection as default
            st.session_state.default_collection = collections[0].name
        else:
            st.session_state.default_collection = None
    return st.session_state.default_collection


def set_default_collection(name: str):
    """Set the default collection name."""
    st.session_state.default_collection = name


def get_collection(name: str = None):
    """Get an existing ChromaDB collection.

    Args:
        name: Collection name. If None, uses the default collection.

    Returns:
        The ChromaDB collection or None if it doesn't exist
    """
    if name is None:
        name = get_default_collection_name()

    client = get_chroma_client()
    embedding_func = get_embedding_function()

    try:
        collection = client.get_collection(name=name, embedding_function=embedding_func)
        return collection
    except ValueError:
        return None


def create_collection(name: str):
    """Create a new ChromaDB collection.

    Args:
        name: Collection name to create

    Returns:
        The newly created ChromaDB collection
    """
    print(f"Creating collection: {name}")
    client = get_chroma_client()
    embedding_func = get_embedding_function()

    try:
        collection = client.create_collection(
            name=name, embedding_function=embedding_func
        )
        return collection
    except ValueError as e:
        # Collection might already exist
        st.error(f"Error creating collection: {str(e)}")
        return None


def get_or_create_collection(name: str = None):
    """Get or create a ChromaDB collection.

    This function is maintained for backward compatibility.

    Args:
        name: Collection name. If None, uses default collection.

    Returns:
        ChromaDB collection
    """
    if name is None:
        name = get_default_collection_name()

    collection = get_collection(name)
    if collection is None:
        collection = create_collection(name)
    return collection


def list_collections():
    """List all available collections.

    Returns:
        List of collection names
    """
    client = get_chroma_client()
    return client.list_collections()


def add_documents(documents: List[Dict[str, Any]], collection_name: str = None):
    """Add documents to the ChromaDB collection."""
    if collection_name is None:
        collection_name = get_default_collection_name()

    collection = get_or_create_collection(collection_name)

    # Prepare the data
    ids = [
        f"doc_{i}_{documents[i]['metadata'].get('source', 'unknown')}_{documents[i]['metadata'].get('chunk', i)}"
        for i in range(len(documents))
    ]
    texts = [doc["text"] for doc in documents]
    metadatas = [doc["metadata"] for doc in documents]

    # Add documents to the collection
    collection.add(ids=ids, documents=texts, metadatas=metadatas)

    return len(documents)


def query_collection(query_text: str, n_results: int = 5, collection_name: str = None):
    """Query the ChromaDB collection for relevant documents."""
    if collection_name is None:
        collection_name = get_default_collection_name()

    collection = get_or_create_collection(collection_name)

    # Query the collection
    results = collection.query(query_texts=[query_text], n_results=n_results)

    return results


def get_all_documents(collection_name: str = None):
    """Get all documents from the collection.

    Returns:
        Dict containing documents, ids, metadatas, and embeddings
    """
    if collection_name is None:
        collection_name = get_default_collection_name()

    collection = get_or_create_collection(collection_name)

    # Get all documents (limited to 1000 by default in ChromaDB)
    results = collection.get()

    return results


def get_document_sources(collection_name: str = None):
    """Get a dictionary of document sources with their chunk counts.

    Returns:
        Dict: {source_name: {"chunks": count}}
    """
    if collection_name is None:
        collection_name = get_default_collection_name()

    collection = get_or_create_collection(collection_name)
    results = collection.get()

    sources = {}
    if results and "metadatas" in results and results["metadatas"]:
        for metadata in results["metadatas"]:
            if "source" in metadata:
                source = metadata["source"]
                if source not in sources:
                    sources[source] = {"chunks": 0}
                sources[source]["chunks"] += 1

    return sources


def delete_document(source: str, collection_name: str = None):
    """Delete all chunks from a specific document source.

    Args:
        source: The document source name to delete
        collection_name: Name of the collection

    Returns:
        int: Number of chunks deleted
    """
    if collection_name is None:
        collection_name = get_default_collection_name()

    collection = get_or_create_collection(collection_name)

    # Get documents with the specified source
    results = collection.get(where={"source": source})

    if results and "ids" in results and results["ids"]:
        # Delete the documents
        collection.delete(ids=results["ids"])
        return len(results["ids"])

    return 0


def clear_collection(collection_name: str = None):
    """Delete all documents in a collection.

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if collection_name is None:
            collection_name = get_default_collection_name()

        collection = get_or_create_collection(collection_name)
        collection.delete()
        return True
    except Exception:
        return False


def delete_collection(name: str):
    """Delete a collection.

    Args:
        name: Name of collection to delete

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        client = get_chroma_client()
        client.delete_collection(name)
        return True
    except Exception:
        return False
