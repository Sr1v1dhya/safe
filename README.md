# S.A.F.E. - Smart AI First Aid Emergency Assistant

## Overview

S.A.F.E. is an intelligent first aid assistant that uses cutting-edge AI technology to provide immediate emergency guidance in multiple languages. The application is designed to be accessible to diverse users, including laborers and non-native speakers, offering critical first aid instructions through text, image, and voice interactions.

## Features

- **Multi-modal Input**: Accept text, images, and voice for describing emergency situations
- **Multilingual Support**: Interface and responses available in English, Tamil, Hindi, and Telugu
- **AI-Powered First Aid Guidance**: Leverages Gemini and Groq for accurate first aid instructions
- **Speech Recognition**: Uses Groq's Whisper API for hands-free operation during emergencies
- **Nearby Medical Facilities**: Integrates with OpenStreetMap API to locate hospitals near the user
- **Knowledge Base Management**: Upload and manage first aid documentation and resources
- **Responsive UI**: Built with Streamlit for a clean, accessible interface across devices

## Technology Stack

- **Frontend**: Streamlit
- **AI Models**:
  - Gemini (Text/Image understanding and response generation)
  - Whisper via Groq (Speech-to-text transcribing)
- **Mapping**: OpenStreetMap API
- **Database**: Vector store for knowledge management

## How It Works

1. **Emergency Input**:
   - Users can describe their emergency situation through text
   - Upload an image of an injury or situation
   - Record voice instructions for hands-free operation

2. **AI Processing**:
   - The system analyzes the input using Gemini's multimodal capabilities
   - Voice inputs are transcribed using Groq's Whisper implementation
   - Query is enhanced with relevant information from the knowledge base

3. **Response Generation**:
   - Clear first aid instructions are provided based on the emergency
   - All guidance follows medically sound principles
   - Responses are delivered in the user's chosen language

4. **Hospital Locator**:
   - If needed, the system displays nearby medical facilities
   - Uses OpenStreetMap API to provide location-based guidance


## Knowledge Base Management

The application includes a robust knowledge base system that:
- Allows uploading of first aid documents (PDFs, DOCx, TXT)
- Organizes information into collections
- Processes and indexes documents for rapid retrieval
- Enhances AI responses with authoritative first aid information

## Installation & Setup

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Configure API keys in Streamlit secrets:
   ```
   gen_ai_api_key: "your_gemini_api_key"
   groq_api_key: "your_groq_api_key"
   ```
4. Run the application:
   ```
   streamlit run app.py
   ```

## Use Cases

- **Construction sites**: Workers can quickly get first aid guidance for common injuries
- **Remote Rural areas**: Access to medical knowledge where healthcare facilities are distant
- **Multilingual communities**: Breaking language barriers in emergency situations
- **Educational settings**: Teaching proper first aid techniques
- **Home safety**: Quick reference for family emergencies

## Future Enhancements

- Offline functionality for areas with limited connectivity (including offline mobile app)
- Adding youtube API for embedded video links in the chatbot
- Adding Whatsapp API for Emergency SOS
- Adding more languages
- Mobile app development
