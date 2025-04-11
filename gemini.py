import json
from PIL import Image
import streamlit as st
from google import genai
from google.genai.types import Content, Part, UserContent, GenerateContentConfig
import speech_recognition as sr
import requests


system_prompt = """ 
You are first-aid assistant named S.A.F.E. (Smart AI First-aid Expert). You have to respond to the user's questions about first-aid. Users will be asking you questions about their medical situation and emergency. 
You have to provide them with the best possible first-aid advice. You are not a doctor, so you should not give any medical advice. You should only provide first-aid advice.
For each question, you'll be given a context that might help you answer it.
Using the context given you can refine and prepare your answer and present it in a friendly and informative manner in detail with step-by-step instructions if needed.
If the context doesn't contain relevant information, you can answer based on your knowledge, but please indicate when you're doing so.
Your response should be properly formated using markdown and should emphasize important information by using bold text.
Follow the below output format.

OUTPUT FORMAT:
    [your response here]

    SEVERITY: [Low|Medium|High] (only show severity after assessing the situation and don't show it in the followup questions)
"""

MODEL_NAME = "gemini-2.0-flash"


# Initialize the Google GenAI client with caching
@st.cache_resource
def initialize_gen_ai_client(api_key):
    client = genai.Client(api_key=api_key)
    return client


@st.cache_resource
def initialze_2nd_gen_ai_client(api_key):
    """Initialize the Google GenAI client with caching."""
    client = genai.Client(api_key=api_key)
    return client


def create_chat(client, history=None):
    """Create a new chat session, optionally with history."""

    # Restore chat history if provided
    if history:
        # Reconstruct Content objects
        contents = []
        for msg in history:
            role = msg["role"]
            parts_list = []

            for part in msg["parts"]:
                if part["text"]:
                    parts_list.append(Part(text=part["text"]))

            contents.append(Content(role=role, parts=parts_list))
        chat = client.chats.create(
            model=MODEL_NAME,
            history=contents,
            config=GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.5,
            ),
        )

    else:
        chat = client.chats.create(
            model=MODEL_NAME,
            config=GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.5,
            ),
        )
    return chat


def get_response(chat, prompt):
    parts = [prompt.text] if prompt.text else []
    for file_content in prompt.files if hasattr(prompt, "files") else []:
        img = Image.open(file_content)
        parts.append(img)

    response = chat.send_message(parts)
    return response.text, chat.get_history()


def get_image_descrption(files):
    """
    Get image description using Google GenAI
    """
    client = initialze_2nd_gen_ai_client(st.secrets["gen_ai_api_key"])
    parts = []
    for file in files:
        image = Image.open(file)
        parts.append(image)

    sys_instruction = """
    You are an image description assistant. You have to describe the images given to you in detail but try to keep it short.
    Your output should be like this:
    Example:
        Image 1: [description of image 1]
        Image 2: [description of image 2]
        ...
    Don't use any other format. Just give the description of the images in the above format.
    """

    # Create a chat session with the system prompt
    response = client.models.generate_content(
        model=MODEL_NAME,
        config=GenerateContentConfig(
            system_instruction=sys_instruction,
            temperature=0.1,
        ),
        contents=parts,
    )

    return response.text
    # return ""

def transcribe_speech(api_key: str) -> str:
    """
    Capture real-time speech from the microphone and transcribe it using Whisper AI API.
    """
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening... Speak now.")
        try:
            audio = recognizer.listen(source, timeout=5)  # Listen for 5 seconds
            st.info("Processing your speech...")
            
            # Convert audio to WAV format and send to Whisper API
            audio_data = audio.get_wav_data()
            response = requests.post(
                "https://api.openai.com/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {api_key}"},
                files={"file": ("speech.wav", audio_data, "audio/wav")},
                data={"model": "whisper-1"}
            )
            response.raise_for_status()
            return response.json().get("text", "Could not transcribe speech.")
        except sr.WaitTimeoutError:
            st.error("Listening timed out. Please try again.")
        except Exception as e:
            st.error(f"Error during transcription: {e}")
        return ""