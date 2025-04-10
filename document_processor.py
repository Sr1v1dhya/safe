import os
import fitz  # PyMuPDF
import streamlit as st
from typing import List, Dict, Any


def extract_text_from_pdf(pdf_file) -> str:
    """Extract text from a PDF file."""
    text = ""
    try:
        # Open the PDF file
        pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
        
        # Iterate through pages
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            text += page.get_text()
            
        pdf_document.close()
        return text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        return ""


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
    """Split text into chunks with overlap."""
    chunks = []
    if len(text) <= chunk_size:
        chunks.append(text)
    else:
        for i in range(0, len(text), chunk_size - overlap):
            chunk = text[i:i + chunk_size]
            if len(chunk) >= chunk_size // 2:  # Only add if chunk is substantial
                chunks.append(chunk)
    return chunks


def process_document(file, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """Process a document and return chunks with metadata."""
    if file.type == "application/pdf":
        text = extract_text_from_pdf(file)
    elif file.type.startswith("text/"):
        text = file.getvalue().decode("utf-8")
    else:
        st.error(f"Unsupported file type: {file.type}")
        return []
        
    chunks = chunk_text(text)
    
    # Create documents with metadata
    documents = []
    base_metadata = metadata or {"source": file.name}
    
    for i, chunk in enumerate(chunks):
        doc = {
            "text": chunk,
            "metadata": {
                **base_metadata,
                "chunk": i
            }
        }
        documents.append(doc)
    
    return documents