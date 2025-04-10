import streamlit as st
from vector_store import query_collection
from typing import List, Dict, Any


def format_context(results: Dict[str, Any]) -> str:
    """Format the query results into a context string."""
    if not results or not results["documents"]:
        return ""

    docs = results["documents"][0]
    metadatas = results["metadatas"][0]

    context_parts = []

    for i, (doc, metadata) in enumerate(zip(docs, metadatas)):
        source = metadata.get("source", "Unknown source")
        context_parts.append(f"[Document: {source}]\n{doc}\n")

    return "\n".join(context_parts)


def generate_prompt_with_context(query: str, results: Dict[str, Any]) -> str:
    """Generate a prompt that includes context for the AI."""
    context = format_context(results)

    if not context:
        return query

    prompt = f"""Answer the question based on the context provided.
    
CONTEXT:
{context}

QUESTION:
{query}
"""
    return prompt
