import streamlit as st
import importlib.util
import os
from streamlit_extras.badges import badge

# Language configuration
LANGUAGES = {
    "en": "English",
    "ta": "Tamil",
    "hi": "Hindi",
    "te": "Telugu"
}

# UI translations for homepage
UI_TRANSLATIONS = {
    "en": {
        "app_title": "S.A.F.E. Chatbot",
        "app_subtitle": "Your Secure AI-powered Assistant for document analysis and intelligent conversations. Upload your documents, ask questions, and get accurate answers powered by advanced AI.",
        "key_features": "Key Features",
        "chatbot_title": "SAFE Chatbot",
        "chatbot_desc": "Ask questions using multi-modal inputs and get answers based on medically certified first aid manuals.",
        "hospitals_title": "Nearby Hospitals",
        "hospitals_desc": "Lists nearby Hospitals based on your location along with a map link to the hospitals.",
        "get_started": "Get Started",
        "how_to_use": "How to use the S.A.F.E. App",
        "step1": "Choose Your Input Mode: Select from audio, image, or text to ask your question.",
        "step2": "Start Chatting: Go to the Chatbot section to interact with the AI.",
        "step3": "Receive Verified Answers: Get responses based on certified first aid manuals and reliable medical sources.",
        "step4": "Find Nearby Help: Use the Maps feature to locate the closest hospitals or medical centers.",
        "step5": "Stay Informed: Explore the Statistics page to view usage trends and common queries.",
        "footer_text": "S.A.F.E. Chatbot v1.0 | Secure AI For Everyone",
        "github": "GitHub",
        "support": "Support",
        "language": "Language"
    },
    "ta": {
        "app_title": "S.A.F.E. சாட் பாட்",
        "app_subtitle": "ஆவண பகுப்பாய்வு மற்றும் புத்திசாலித்தனமான உரையாடல்களுக்கான உங்கள் பாதுகாப்பான AI-செயலாக்கப்பட்ட உதவியாளர். உங்கள் ஆவணங்களை பதிவேற்றவும், கேள்விகள் கேட்கவும், மேம்பட்ட AI மூலம் துல்லியமான பதில்களைப் பெறவும்.",
        "key_features": "முக்கிய அம்சங்கள்",
        "chatbot_title": "SAFE சாட் பாட்",
        "chatbot_desc": "பல்முறை உள்ளீடுகளைப் பயன்படுத்தி கேள்விகளைக் கேட்கவும், மருத்துவமாக சான்றளிக்கப்பட்ட முதலுதவி கையேடுகளின் அடிப்படையில் பதில்களைப் பெறவும்.",
        "hospitals_title": "அருகிலுள்ள மருத்துவமனைகள்",
        "hospitals_desc": "உங்கள் இருப்பிடத்தின் அடிப்படையில் அருகிலுள்ள மருத்துவமனைகளை பட்டியலிடுகிறது, மருத்துவமனைகளுக்கான வரைபட இணைப்புடன்.",
        "get_started": "தொடங்கவும்",
        "how_to_use": "S.A.F.E. ஆப்பை எவ்வாறு பயன்படுத்துவது",
        "step1": "உங்கள் உள்ளீட்டு பயன்முறையைத் தேர்ந்தெடுக்கவும்: உங்கள் கேள்வியைக் கேட்க ஒலி, படம் அல்லது உரையிலிருந்து தேர்ந்தெடுக்கவும்.",
        "step2": "சாட்யைத் தொடங்கவும்: AI உடன் தொடர்புகொள்ள சாட் பாட் பிரிவுக்குச் செல்லவும்.",
        "step3": "சரிபார்க்கப்பட்ட பதில்களைப் பெறவும்: சான்றளிக்கப்பட்ட முதலுதவி கையேடுகள் மற்றும் நம்பகமான மருத்துவ ஆதாரங்களின் அடிப்படையில் பதில்களைப் பெறவும்.",
        "step4": "அருகிலுள்ள உதவியைக் கண்டறியவும்: அருகிலுள்ள மருத்துவமனைகள் அல்லது மருத்துவ மையங்களைக் கண்டறிய வரைபடங்கள் அம்சத்தைப் பயன்படுத்தவும்.",
        "step5": "தகவல் அறிந்திருங்கள்: பயன்பாட்டு போக்குகள் மற்றும் பொதுவான கேள்விகளைக் காண புள்ளிவிவரங்கள் பக்கத்தை ஆராயுங்கள்.",
        "footer_text": "S.A.F.E. சாட் பாட் v1.0 | அனைவருக்கும் பாதுகாப்பான AI",
        "github": "GitHub",
        "support": "ஆதரவு",
        "language": "மொழி"
    },
    "hi": {
        "app_title": "S.A.F.E. चैटबॉट",
        "app_subtitle": "दस्तावेज़ विश्लेषण और बुद्धिमान वार्तालापों के लिए आपका सुरक्षित AI-संचालित सहायक। अपने दस्तावेज़ अपलोड करें, प्रश्न पूछें और उन्नत AI द्वारा संचालित सटीक उत्तर प्राप्त करें।",
        "key_features": "मुख्य विशेषताएँ",
        "chatbot_title": "SAFE चैटबॉट",
        "chatbot_desc": "मल्टी-मोडल इनपुट का उपयोग करके प्रश्न पूछें और चिकित्सकीय रूप से प्रमाणित प्राथमिक चिकित्सा पुस्तिकाओं के आधार पर उत्तर प्राप्त करें।",
        "hospitals_title": "आस-पास के अस्पताल",
        "hospitals_desc": "आपके स्थान के आधार पर आस-पास के अस्पतालों की सूची बनाता है, अस्पतालों के मानचित्र लिंक के साथ।",
        "get_started": "शुरू करें",
        "how_to_use": "S.A.F.E. ऐप का उपयोग कैसे करें",
        "step1": "अपना इनपुट मोड चुनें: अपना प्रश्न पूछने के लिए ऑडियो, छवि या टेक्स्ट में से चुनें।",
        "step2": "चैटिंग शुरू करें: AI के साथ बातचीत करने के लिए चैटबॉट अनुभाग पर जाएं।",
        "step3": "सत्यापित उत्तर प्राप्त करें: प्रमाणित प्राथमिक चिकित्सा पुस्तिकाओं और विश्वसनीय चिकित्सा स्रोतों के आधार पर प्रतिक्रियाएँ प्राप्त करें।",
        "step4": "आस-पास की मदद खोजें: नजदीकी अस्पतालों या चिकित्सा केंद्रों का पता लगाने के लिए मानचित्र सुविधा का उपयोग करें।",
        "step5": "जानकारी रखें: उपयोग रुझानों और सामान्य प्रश्नों को देखने के लिए सांख्यिकी पृष्ठ का अन्वेषण करें।",
        "footer_text": "S.A.F.E. चैटबॉट v1.0 | सभी के लिए सुरक्षित AI",
        "github": "GitHub",
        "support": "सहायता",
        "language": "भाषा"
    },
    "te": {
        "app_title": "S.A.F.E. చాట్‌బాట్",
        "app_subtitle": "డాక్యుమెంట్ విశ్లేషణ మరియు తెలివైన సంభాషణల కోసం మీ సురక్షిత AI-ఆధారిత అసిస్టెంట్. మీ పత్రాలను అప్‌లోడ్ చేయండి, ప్రశ్నలు అడగండి మరియు అధునాతన AI ద్వారా ఖచ్చితమైన సమాధానాలను పొందండి.",
        "key_features": "ముఖ్య ఫీచర్లు",
        "chatbot_title": "SAFE చాట్‌బాట్",
        "chatbot_desc": "మల్టీ-మోడల్ ఇన్‌పుట్‌లను ఉపయోగించి ప్రశ్నలు అడగండి మరియు వైద్యపరంగా ధృవీకరించబడిన ప్రథమ చికిత్స పుస్తకాల ఆధారంగా సమాధానాలు పొందండి.",
        "hospitals_title": "సమీప ఆసుపత్రులు",
        "hospitals_desc": "మీ స్థానం ఆధారంగా సమీప ఆసుపత్రులను జాబితా చేస్తుంది, ఆసుపత్రులకు మ్యాప్ లింక్‌తో పాటు.",
        "get_started": "ప్రారంభించండి",
        "how_to_use": "S.A.F.E. యాప్‌ని ఎలా ఉపయోగించాలి",
        "step1": "మీ ఇన్‌పుట్ మోడ్‌ని ఎంచుకోండి: మీ ప్రశ్నను అడగడానికి ఆడియో, చిత్రం లేదా టెక్స్ట్ నుండి ఎంచుకోండి.",
        "step2": "చాటింగ్ ప్రారంభించండి: AI తో సంభాషించడానికి చాట్‌బాట్ విభాగానికి వెళ్లండి.",
        "step3": "ధృవీకరించబడిన సమాధానాలు పొందండి: ధృవీకరించబడిన ప్రథమ చికిత్స మాన్యువల్స్ మరియు విశ్వసనీయమైన వైద్య వనరుల ఆధారంగా సమాధానాలు పొందండి.",
        "step4": "సమీప సహాయాన్ని కనుగొనండి: సమీప ఆసుపత్రులు లేదా వైద్య కేంద్రాలను కనుగొనడానికి మ్యాప్స్ ఫీచర్‌ని ఉపయోగించండి.",
        "step5": "సమాచారం తెలుసుకోండి: వినియోగ ధోరణులు మరియు సాధారణ ప్రశ్నలను వీక్షించడానికి స్టాటిస్టిక్స్ పేజీని అన్వేషించండి.",
        "footer_text": "S.A.F.E. చాట్‌బాట్ v1.0 | అందరికీ సురక్షితమైన AI",
        "github": "GitHub",
        "support": "మద్దతు",
        "language": "భాష"
    }
}

# Initialize session state for language if not exists
if 'language' not in st.session_state:
    st.session_state.language = 'en'  # Default to English

# Get URL query params early
params = st.query_params
hidden_page = params.get("page")

# Only call set_page_config here if NOT loading a hidden page
if hidden_page not in ["Data_Upload", "Statistics"]:
    st.set_page_config(
        page_title="SAFE App",
        page_icon="🛡", 
        layout="wide",
        initial_sidebar_state="expanded"  # Make sure sidebar is expanded
    )

# Ensure the sidebar is shown by adding some content before language selector
# This helps avoid issues where the sidebar might not be visible
st.sidebar.image("firstaid.png", width=80)

# Add a prominent language selector to the sidebar with clear highlighting
with st.sidebar:
    st.markdown("### 🌐 " + UI_TRANSLATIONS[st.session_state.language]["language"])
    
    # Add some space and a container with a border to make it stand out
    with st.container(border=True):
        selected_language = st.selectbox(
            "Select your preferred language",
            options=list(LANGUAGES.keys()),
            format_func=lambda x: LANGUAGES[x],
            index=list(LANGUAGES.keys()).index(st.session_state.language),
            key="language_selector"  # Adding a unique key
        )
    
    # Update session state when language changes
    if selected_language != st.session_state.language:
        st.session_state.language = selected_language
        st.rerun()  # Rerun the app to reflect language changes
    
    # Add a separator after the language selector
    st.divider()

# Get current UI translations
ui = UI_TRANSLATIONS[st.session_state.language]

# Custom CSS for better styling
st.markdown("""
    <style>
        .main {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        .stButton>button {
            border-radius: 8px;
            padding: 0.5rem 1rem;
        }
        .stTextInput>div>div>input {
            border-radius: 8px;
            padding: 0.5rem 1rem;
        }
        .welcome-header {
            font-size: 2.5rem !important;
            margin-bottom: 1rem;
        }
        .feature-card {
            border-radius: 10px;
            padding: 1.5rem;
            background-color: #f0f2f6;
            margin-bottom: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .feature-icon {
            font-size: 1.8rem;
            margin-bottom: 0.5rem;
        }
        .divider {
            margin: 2rem 0;
            border-top: 1px solid #e1e4e8;
        }
        .footer {
            margin-top: 3rem;
            text-align: center;
            color: #666;
            font-size: 0.9rem;
        }
        .streamlit-expanderHeader {
            font-size: 20px !important;
        }
        /* Make sidebar more prominent */
        [data-testid="stSidebar"] {
            background-color: #000000;
            border-right: 1px solid #eaeaea;
        }
        /* Make language selector stand out */
        div[data-testid="stSelectbox"] {
            margin-bottom: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

# Route to hidden pages
if hidden_page in ["Data_Upload", "Statistics"]:
    file_path = f"hidden_pages/{hidden_page}.py"
    if os.path.exists(file_path):
        spec = importlib.util.spec_from_file_location("hidden_module", file_path)
        hidden_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(hidden_module)
        hidden_module.main()  # assumes each hidden page defines main()
    else:
        st.set_page_config(page_title="Error", layout="centered")  
        st.error("Page not found")
else:
    # Default homepage UI with improved layout
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f'<h1 class="welcome-header">🆘 {ui["app_title"]}</h1>', unsafe_allow_html=True)
        st.markdown(ui["app_subtitle"])
    
    with col2:
        st.image("firstaid.png", width=150)  # Replace with your logo
    
    st.divider()
    
    # Feature cards
    st.subheader(ui["key_features"])
    cols = st.columns(2)
    
    with cols[0]:
        with st.container(border=True):
            st.markdown('<div class="feature-icon">💬</div>', unsafe_allow_html=True)
            st.markdown(f'<a href="/Chat_Bot" target="_self" style="text-decoration: none;"><strong>{ui["chatbot_title"]}</strong></a>',unsafe_allow_html=True)
            st.markdown(ui["chatbot_desc"])
    with cols[1]:
        with st.container(border=True):
            st.markdown('<div class="feature-icon">🏥</div>', unsafe_allow_html=True)
            st.markdown(f'<a href="/Hospitals" target="_self" style="text-decoration: none;"><strong>{ui["hospitals_title"]}</strong></a>',unsafe_allow_html=True)
            st.markdown(ui["hospitals_desc"])
    
    st.divider()
    
    
    # Quick start section
    st.subheader(ui["get_started"])
    with st.expander(ui["how_to_use"], expanded=True):
        st.markdown(f"""
        1. **{ui["step1"]}**
        2. **{ui["step2"]}**
        3. **{ui["step3"]}**
        4. **{ui["step4"]}**
        5. **{ui["step5"]}**
        """)

   
    
    # Footer
    st.markdown(f"""
        <div class="footer">
            <p>{ui["footer_text"]}</p>
            <div style="margin-top: 0.5rem;">
                <a href="https://github.com/Sr1v1dhya/safe" target="_blank">{ui["github"]}</a> |  
                <a href="mailto:sharon23110444@snuchennai.edu.in">{ui["support"]}</a>
            </div>
        </div>
    """, unsafe_allow_html=True)