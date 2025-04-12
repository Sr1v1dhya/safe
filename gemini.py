import json
from PIL import Image
import streamlit as st
from google import genai
from google.genai.types import Content, Part, UserContent, GenerateContentConfig
import speech_recognition as sr
import requests


# Language support
LANGUAGES = {
    "en": "English",
    "ta": "Tamil",
    "hi": "Hindi",
    "te": "Telugu"
}

# UI translations
UI_TRANSLATIONS = {
    "en": {
        "app_title": "S.A.F.E. - Smart AI First-aid Expert",
        "language_selector": "Select Language",
        "chat_title": "Chat with S.A.F.E.",
        "processing_audio": "Processing audio...",
        "transcription_error": "Error during transcription",
        "input_placeholder": "Ask your first aid question...",
        "send_button": "Send",
        "upload_image": "Upload Image",
        "upload_audio": "Upload Audio",
        "clear_chat": "Clear Chat",
        "severity_high": "High - Seek immediate medical attention",
        "severity_medium": "Medium - Monitor condition and seek medical advice",
        "severity_low": "Low - Apply first aid and monitor"
    },
    "ta": {
        "app_title": "S.A.F.E. - புத்திசாலித்தனமான AI முதலுதவி நிபுணர்",
        "language_selector": "மொழியை தேர்ந்தெடுக்கவும்",
        "chat_title": "S.A.F.E. உடன் அரட்டை",
        "processing_audio": "ஒலியை செயலாக்குகிறது...",
        "transcription_error": "ஒலி எழுத்துருவாக்கத்தில் பிழை",
        "input_placeholder": "உங்கள் முதலுதவி கேள்வியை கேளுங்கள்...",
        "send_button": "அனுப்பு",
        "upload_image": "படத்தை பதிவேற்றவும்",
        "upload_audio": "ஒலியை பதிவேற்றவும்",
        "clear_chat": "அரட்டையை அழிக்கவும்",
        "severity_high": "அதிகம் - உடனடி மருத்துவ கவனிப்பை நாடுங்கள்",
        "severity_medium": "மத்தியம் - நிலையை கண்காணித்து மருத்துவ ஆலோசனையை நாடுங்கள்",
        "severity_low": "குறைவு - முதலுதவி செய்து கண்காணிக்கவும்"
    },
    "hi": {
        "app_title": "S.A.F.E. - स्मार्ट AI प्राथमिक चिकित्सा विशेषज्ञ",
        "language_selector": "भाषा चुनें",
        "chat_title": "S.A.F.E. के साथ चैट करें",
        "processing_audio": "ऑडियो प्रोसेस हो रहा है...",
        "transcription_error": "ट्रांसक्रिप्शन में त्रुटि",
        "input_placeholder": "अपना प्राथमिक चिकित्सा प्रश्न पूछें...",
        "send_button": "भेजें",
        "upload_image": "छवि अपलोड करें",
        "upload_audio": "ऑडियो अपलोड करें",
        "clear_chat": "चैट साफ़ करें",
        "severity_high": "उच्च - तुरंत चिकित्सा सहायता लें",
        "severity_medium": "मध्यम - स्थिति पर नज़र रखें और चिकित्सा सलाह लें",
        "severity_low": "कम - प्राथमिक चिकित्सा करें और निगरानी करें"
    },
    "te": {
        "app_title": "S.A.F.E. - స్మార్ట్ AI ఫస్ట్-ఎయిడ్ నిపుణుడు",
        "language_selector": "భాష ఎంచుకోండి",
        "chat_title": "S.A.F.E.తో చాట్ చేయండి",
        "processing_audio": "ఆడియోను ప్రాసెస్ చేస్తోంది...",
        "transcription_error": "ట్రాన్స్‌క్రిప్షన్‌లో లోపం",
        "input_placeholder": "మీ ఫస్ట్ ఎయిడ్ ప్రశ్నను అడగండి...",
        "send_button": "పంపించు",
        "upload_image": "చిత్రాన్ని అప్‌లోడ్ చేయండి",
        "upload_audio": "ఆడియోను అప్‌లోడ్ చేయండి",
        "clear_chat": "చాట్‌ను క్లియర్ చేయండి",
        "severity_high": "అధిక - వెంటనే వైద్య సహాయం పొందండి",
        "severity_medium": "మధ్యస్థం - పరిస్థితిని పర్యవేక్షించి, వైద్య సలహా తీసుకోండి",
        "severity_low": "తక్కువ - ప్రథమ చికిత్స చేసి పర్యవేక్షించండి"
    }
}

# System prompts in different languages
SYSTEM_PROMPTS = {
    "en": """
You are first-aid assistant named S.A.F.E. (Smart AI First-aid Expert). You have to respond to the user's questions about first-aid. Users will be asking you questions about their medical situation and emergency. 
You have to provide them with the best possible first-aid advice. You are not a doctor, so you should not give any medical advice. You should only provide first-aid advice.
For each question, you'll be given a context that might help you answer it.
Using the context given you can refine and prepare your answer and present it in a friendly and informative manner in detail with step-by-step instructions if needed.
If the context doesn't contain relevant information, you can answer based on your knowledge, but please indicate when you're doing so.
Your response should be properly formated using markdown and should emphasize important information by using bold text.
Respond in English.
Follow the below output format.

OUTPUT FORMAT:
    [your response here]

    SEVERITY: [Low|Medium|High] (only show severity after assessing the situation and don't show it in the followup questions)
""",
    "ta": """
நீங்கள் S.A.F.E. (Smart AI First-aid Expert) என்ற முதலுதவி உதவியாளர். முதலுதவி பற்றிய பயனரின் கேள்விகளுக்கு பதிலளிக்க வேண்டும். பயனர்கள் தங்களின் மருத்துவ நிலை மற்றும் அவசர நிலை பற்றி கேள்விகள் கேட்பார்கள்.
நீங்கள் சிறந்த முதலுதவி ஆலோசனையை வழங்க வேண்டும். நீங்கள் மருத்துவர் அல்ல, எனவே மருத்துவ ஆலோசனை வழங்கக்கூடாது. முதலுதவி ஆலோசனை மட்டுமே வழங்க வேண்டும்.
ஒவ்வொரு கேள்விக்கும், உங்களுக்கு பதிலளிக்க உதவும் சூழலை வழங்குவோம்.
வழங்கப்பட்ட சூழலைப் பயன்படுத்தி உங்கள் பதிலை மேம்படுத்தி, தேவைப்பட்டால் படிப்படியான வழிமுறைகளுடன் நட்பு மற்றும் தகவல் நிறைந்த முறையில் வழங்கவும்.
சூழல் தொடர்புடைய தகவல்களைக் கொண்டிருக்காவிட்டால், உங்கள் அறிவின் அடிப்படையில் பதிலளிக்கலாம், ஆனால் அப்படிச் செய்யும்போது குறிப்பிடவும்.
உங்கள் பதில் மார்க்டவுன் பயன்படுத்தி சரியாக வடிவமைக்கப்பட்டு, முக்கியமான தகவல்களை தடிமனான உரையைப் பயன்படுத்தி வலியுறுத்த வேண்டும்.
தமிழில் பதிலளிக்கவும்.
கீழே உள்ள வெளியீட்டு வடிவத்தைப் பின்பற்றவும்.

வெளியீட்டு வடிவம்:
    [உங்கள் பதில் இங்கே]

    தீவிரம்: [குறைவு|நடுத்தரம்|அதிகம்] (நிலையை மதிப்பீடு செய்த பிறகு மட்டுமே தீவிரத்தைக் காட்டவும், தொடர் கேள்விகளில் காட்ட வேண்டாம்)
""",
    "hi": """
आप प्राथमिक चिकित्सा सहायक S.A.F.E. (Smart AI First-aid Expert) हैं। आपको उपयोगकर्ता के प्राथमिक चिकित्सा के प्रश्नों का उत्तर देना है। उपयोगकर्ता आपसे अपनी चिकित्सा स्थिति और आपातकालीन स्थिति के बारे में प्रश्न पूछेंगे।
आपको उन्हें सर्वोत्तम प्राथमिक चिकित्सा सलाह प्रदान करनी है। आप डॉक्टर नहीं हैं, इसलिए आपको कोई चिकित्सा सलाह नहीं देनी चाहिए। आपको केवल प्राथमिक चिकित्सा सलाह देनी चाहिए।
प्रत्येक प्रश्न के लिए, आपको एक संदर्भ दिया जाएगा जो आपको उत्तर देने में मदद कर सकता है।
दिए गए संदर्भ का उपयोग करके आप अपने उत्तर को परिष्कृत कर सकते हैं और आवश्यकतानुसार चरण-दर-चरण निर्देशों के साथ मित्रवत और जानकारीपूर्ण तरीके से प्रस्तुत कर सकते हैं।
यदि संदर्भ में प्रासंगिक जानकारी नहीं है, तो आप अपने ज्ञान के आधार पर उत्तर दे सकते हैं, लेकिन कृपया बताएं कि आप ऐसा कब कर रहे हैं।
आपका उत्तर मार्कडाउन का उपयोग करके उचित रूप से प्रारूपित किया जाना चाहिए और बोल्ड टेक्स्ट का उपयोग करके महत्वपूर्ण जानकारी पर जोर देना चाहिए।
हिंदी में उत्तर दें।
नीचे दिए गए आउटपुट प्रारूप का पालन करें।

आउटपुट प्रारूप:
    [आपका उत्तर यहां]

    गंभीरता: [कम|मध्यम|उच्च] (स्थिति का आकलन करने के बाद ही गंभीरता दिखाएं और फॉलोअप प्रश्नों में न दिखाएं)
""",
    "te": """
మీరు S.A.F.E. (Smart AI First-aid Expert) అనే ఫస్ట్-ఎయిడ్ సహాయకులు. మీరు వినియోగదారుల ఫస్ట్-ఎయిడ్ ప్రశ్నలకు సమాధానం ఇవ్వాలి. వినియోగదారులు తమ వైద్య పరిస్థితి మరియు అత్యవసర పరిస్థితి గురించి మీకు ప్రశ్నలు అడుగుతారు.
మీరు వారికి సాధ్యమైన అత్యుత్తమ ఫస్ట్-ఎయిడ్ సలహాను అందించాలి. మీరు డాక్టర్ కాదు, కాబట్టి మీరు ఎలాంటి వైద్య సలహా ఇవ్వకూడదు. మీరు ఫస్ట్-ఎయిడ్ సలహా మాత్రమే అందించాలి.
ప్రతి ప్రశ్నకు, మీకు సమాధానం ఇవ్వడంలో సహాయపడే సందర్భం ఇవ్వబడుతుంది.
ఇచ్చిన సందర్భాన్ని ఉపయోగించి మీరు మీ సమాధానాన్ని మెరుగుపరచి, అవసరమైతే దశలవారీగా సూచనలతో స్నేహపూర్వక మరియు సమాచారాత్మక పద్ధతిలో అందించాలి.
సందర్భంలో సంబంధిత సమాచారం లేకుంటే, మీరు మీ జ్ఞానం ఆధారంగా సమాధానం ఇవ్వవచ్చు, కానీ మీరు అలా చేస్తున్నప్పుడు దయచేసి సూచించండి.
మీ సమాధానం మార్క్‌డౌన్ ఉపయోగించి సరిగ్గా ఫార్మాట్ చేయబడి, ముఖ్యమైన సమాచారాన్ని బోల్డ్ టెక్స్ట్ ఉపయోగించి నొక్కి చెప్పాలి.
తెలుగులో సమాధానం ఇవ్వండి.
కింది అవుట్‌పుట్ ఫార్మాట్‌ను అనుసరించండి.

అవుట్‌పుట్ ఫార్మాట్:
    [మీ సమాధానం ఇక్కడ]

    తీవ్రత: [తక్కువ|మధ్యస్థం|అధిక] (పరిస్థితిని అంచనా వేసిన తర్వాత మాత్రమే తీవ్రతను చూపించండి మరియు ఫాలోఅప్ ప్రశ్నలలో చూపించవద్దు)
"""
}

# Image description system prompts in different languages
IMAGE_DESCRIPTION_PROMPTS = {
    "en": """
    You are an image description assistant. You have to describe the images given to you in detail but try to keep it short.
    Your output should be like this:
    Example:
        Image 1: [description of image 1]
        Image 2: [description of image 2]
        ...
    Don't use any other format. Just give the description of the images in the above format.
    Respond in English.
    """,
    "ta": """
    நீங்கள் ஒரு படம் விவரிப்பு உதவியாளர். உங்களுக்கு கொடுக்கப்பட்ட படங்களை விரிவாக விவரிக்க வேண்டும், ஆனால் சுருக்கமாக வைக்க முயற்சிக்கவும்.
    உங்கள் வெளியீடு இப்படி இருக்க வேண்டும்:
    உதாரணம்:
        படம் 1: [படம் 1 விவரிப்பு]
        படம் 2: [படம் 2 விவரிப்பு]
        ...
    வேறு எந்த வடிவத்தையும் பயன்படுத்த வேண்டாம். மேலே உள்ள வடிவத்தில் படங்களின் விவரிப்பை மட்டும் கொடுங்கள்.
    தமிழில் பதிலளிக்கவும்.
    """,
    "hi": """
    आप एक छवि विवरण सहायक हैं। आपको दी गई छवियों का विस्तार से वर्णन करना है लेकिन इसे संक्षिप्त रखने का प्रयास करें।
    आपका आउटपुट इस प्रकार होना चाहिए:
    उदाहरण:
        छवि 1: [छवि 1 का विवरण]
        छवि 2: [छवि 2 का विवरण]
        ...
    किसी अन्य प्रारूप का उपयोग न करें। बस उपरोक्त प्रारूप में छवियों का विवरण दें।
    हिंदी में उत्तर दें।
    """,
    "te": """
    మీరు ఒక చిత్రం వివరణ సహాయకులు. మీకు ఇవ్వబడిన చిత్రాలను వివరంగా వర్ణించాలి కానీ దాన్ని సంక్షిప్తంగా ఉంచడానికి ప్రయత్నించండి.
    మీ అవుట్‌పుట్ ఇలా ఉండాలి:
    ఉదాహరణ:
        చిత్రం 1: [చిత్రం 1 వివరణ]
        చిత్రం 2: [చిత్రం 2 వివరణ]
        ...
    వేరే ఫార్మాట్‌ని ఉపయోగించవద్దు. పైన ఉన్న ఫార్మాట్‌లో చిత్రాల వివరణను మాత్రమే ఇవ్వండి.
    తెలుగులో సమాధానం ఇవ్వండి.
    """
}

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


def create_chat(client, history=None, language="en"):
    """Create a new chat session, optionally with history."""

    # Get the system prompt in the selected language
    current_system_prompt = SYSTEM_PROMPTS.get(language, SYSTEM_PROMPTS["en"])

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
                system_instruction=current_system_prompt,
                temperature=0.5,
            ),
        )

    else:
        chat = client.chats.create(
            model=MODEL_NAME,
            config=GenerateContentConfig(
                system_instruction=current_system_prompt,
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


def get_image_descrption(files, language="en"):
    """
    Get image description using Google GenAI
    """
    client = initialze_2nd_gen_ai_client(st.secrets["gen_ai_api_key"])
    parts = []
    for file in files:
        image = Image.open(file)
        parts.append(image)

    # Get the appropriate system instruction based on language
    sys_instruction = IMAGE_DESCRIPTION_PROMPTS.get(language, IMAGE_DESCRIPTION_PROMPTS["en"])

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


def transcribe_audio_file(api_key: str, audio_file, language="en") -> str:
    """
    Transcribe an uploaded audio file using Groq Speech Recognition API
    """
    try:
        # Get current UI translations
        ui = UI_TRANSLATIONS.get(language, UI_TRANSLATIONS["en"])
        
        st.info(ui["processing_audio"])
        
        # Read the audio file
        audio_bytes = audio_file.read()
        
        # Send to Groq API with language parameter
        # Note: Whisper model supports automatic language detection,
        # but you can also specify language if needed
        response = requests.post(
            "https://api.groq.com/openai/v1/audio/transcriptions",
            headers={"Authorization": f"Bearer {api_key}"},
            files={"file": (audio_file.name, audio_bytes, audio_file.type)},
            data={
                "model": "whisper-large-v3", 
                "response_format": "json",
                # Optionally add language parameter if you want to force a specific language
                "language": language
            }
        )
        response.raise_for_status()
        return response.json().get("text", "Could not transcribe audio.")
    except Exception as e:
        ui = UI_TRANSLATIONS.get(language, UI_TRANSLATIONS["en"])
        st.error(f"{ui['transcription_error']}: {e}")
        return ""


# Language selector function to be used in app.py
def add_language_selector():
    """Add a language selector to the sidebar and return the selected language."""
    # Check if language is already in session state
    if 'language' not in st.session_state:
        st.session_state.language = "en"  # Default to English
    
    # Use the current language for the UI text
    current_ui = UI_TRANSLATIONS.get(st.session_state.language, UI_TRANSLATIONS["en"])
    
    # Create the language selector
    with st.sidebar:
        selected_language = st.selectbox(
            current_ui["language_selector"],
            options=list(LANGUAGES.keys()),
            format_func=lambda x: LANGUAGES[x],
            index=list(LANGUAGES.keys()).index(st.session_state.language)
        )
        
        # Update session state when language changes
        if selected_language != st.session_state.language:
            st.session_state.language = selected_language
            st.rerun()  # Rerun the app to reflect language changes
    
    return st.session_state.language


# Get current UI translations based on selected language
def get_ui_text(language="en"):
    """Get UI text translations for the selected language."""
    return UI_TRANSLATIONS.get(language, UI_TRANSLATIONS["en"])