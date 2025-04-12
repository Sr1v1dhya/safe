import sqlite3
import json
from datetime import datetime
import os
import streamlit as st


def get_db_connection():
    """Create a connection to the SQLite database."""
    # Ensure the data directory exists
    os.makedirs("data", exist_ok=True)

    conn = sqlite3.connect("data/chats.db")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the database with required tables."""
    conn = get_db_connection()
    c = conn.cursor()

    # Create table for chat sessions
    c.execute(
        """
    CREATE TABLE IF NOT EXISTS chat_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """
    )

    # Create table for messages within chat sessions
    c.execute(
        """
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        images BLOB,
        timestamp TEXT NOT NULL,
        FOREIGN KEY (session_id) REFERENCES chat_sessions (id) ON DELETE CASCADE
    )
    """
    )

    # Create table for gemini chat history
    c.execute(
        """
    CREATE TABLE IF NOT EXISTS gemini_history (
        session_id INTEGER NOT NULL,
        history_data TEXT NOT NULL,
        FOREIGN KEY (session_id) REFERENCES chat_sessions (id) ON DELETE CASCADE
    )
    """
    )

    conn.commit()
    conn.close()


def create_new_chat():
    """Create a new chat session and return its ID."""
    conn = get_db_connection()
    c = conn.cursor()

    now = datetime.now().isoformat()
    title = "New Chat"  # Changed from timestamp to "New Chat"

    c.execute(
        "INSERT INTO chat_sessions (title, created_at, updated_at) VALUES (?, ?, ?)",
        (title, now, now),
    )

    session_id = c.lastrowid
    conn.commit()
    conn.close()

    return session_id


def update_chat_title(session_id, title):
    """Update the title of a chat session."""
    conn = get_db_connection()
    c = conn.cursor()

    now = datetime.now().isoformat()

    c.execute(
        "UPDATE chat_sessions SET title = ?, updated_at = ? WHERE id = ?",
        (title, now, session_id),
    )

    conn.commit()
    conn.close()


def get_chat_sessions():
    """Retrieve all chat sessions."""
    conn = get_db_connection()
    c = conn.cursor()

    c.execute(
        "SELECT id, title, created_at FROM chat_sessions ORDER BY updated_at DESC"
    )
    sessions = [dict(row) for row in c.fetchall()]

    conn.close()
    return sessions


def save_message(session_id, role, content, images=None):
    """Save a message to the database."""
    conn = get_db_connection()
    c = conn.cursor()

    now = datetime.now().isoformat()

    # Convert images to JSON string if present
    img_data = None
    if images:
        img_data = json.dumps([img.hex() for img in images])

    c.execute(
        "INSERT INTO messages (session_id, role, content, images, timestamp) VALUES (?, ?, ?, ?, ?)",
        (session_id, role, content, img_data, now),
    )

    # Update the chat session's updated_at timestamp
    c.execute("UPDATE chat_sessions SET updated_at = ? WHERE id = ?", (now, session_id))

    conn.commit()
    conn.close()


def get_messages(session_id):
    """Retrieve all messages for a chat session."""
    conn = get_db_connection()
    c = conn.cursor()

    c.execute(
        "SELECT role, content, images FROM messages WHERE session_id = ? ORDER BY timestamp",
        (session_id,),
    )
    messages = []

    for row in c.fetchall():
        message = {"role": row["role"], "content": row["content"]}
        if row["images"]:
            # Convert from JSON string back to list of bytes
            images = [bytes.fromhex(img) for img in json.loads(row["images"])]
            message["images"] = images
        else:
            message["images"] = []
        messages.append(message)

    conn.close()
    return messages


def save_gemini_history(session_id, history_data):
    """Save Gemini chat history for a session."""
    conn = get_db_connection()
    c = conn.cursor()

    # Convert Content objects to serializable form
    serializable_history = []
    for content in history_data:
        parts_data = []
        for part in content.parts:
            part_data = {"text": part.text if part.text else None}
            parts_data.append(part_data)

        serializable_history.append({"role": content.role, "parts": parts_data})

    history_json = json.dumps(serializable_history)

    # Delete any existing history for this session
    c.execute("DELETE FROM gemini_history WHERE session_id = ?", (session_id,))

    # Insert the new history
    c.execute(
        "INSERT INTO gemini_history (session_id, history_data) VALUES (?, ?)",
        (session_id, history_json),
    )

    conn.commit()
    conn.close()


def get_gemini_history(session_id):
    """Retrieve Gemini chat history for a session."""
    conn = get_db_connection()
    c = conn.cursor()

    c.execute(
        "SELECT history_data FROM gemini_history WHERE session_id = ?", (session_id,)
    )
    row = c.fetchone()

    conn.close()

    if row:
        return json.loads(row["history_data"])
    return None


def delete_chat_session(chat_id):
    """Delete a specific chat session and all its messages"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chat_sessions WHERE id = ?", (chat_id,))
    conn.commit()
    conn.close()


def delete_all_chat_sessions():
    """Delete all chat sessions and messages"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chat_sessions")
    conn.commit()
    conn.close()