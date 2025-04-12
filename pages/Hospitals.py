import streamlit as st
import requests
from geopy.distance import geodesic
import time
import folium
from streamlit_folium import folium_static

# Language configuration - match the home.py file
LANGUAGES = {
    "en": "English",
    "ta": "Tamil",
    "hi": "Hindi",
    "te": "Telugu"
}

# UI translations for the hospitals page - fixed syntax from the original
UI_TRANSLATIONS = {
    "ta": {
        "page_title": "அருகிலுள்ள மருத்துவமனைகள்",
        "page_icon": "🏥",
        "app_header": "<h1>🏥 அருகிலுள்ள மருத்துவமனைகள்</h1>",
        "app_description": "<div class=\"app-description\">உங்கள் தற்போதைய இருப்பிடத்திற்கு அருகில் உள்ள மருத்துவமனைகளைக் கண்டறியவும். இந்த பயன்பாடு OpenStreetMap தரவைப் பயன்படுத்தி உங்களைச் சுற்றியுள்ள மருத்துவ வசதிகளைக் கண்டறிந்து தூர தகவல்களை வழங்குகிறது.</div>",
        "settings_panel": "⚙️ தேடல் அமைப்புகள்",
        "search_radius": "தேடல் ஆரம் (கி.மீ)",
        "maximum_results": "அதிகபட்ச முடிவுகள்",
        "detect_location_button": "📍 எனது இருப்பிடத்தைக் கண்டறி",
        "refresh_button": "🔄 முடிவுகளைப் புதுப்பி",
        "detecting_location": "உங்கள் இருப்பிடத்தைக் கண்டறிகிறது...",
        "your_location": "<strong>📍 உங்கள் இருப்பிடம்:</strong> {0:.6f}, {1:.6f}<br><small>{2} கி.மீ ஆரத்திற்குள் மருத்துவமனைகளைத் தேடுகிறது</small>",
        "searching_hospitals": "🔍 அருகிலுள்ள மருத்துவமனைகளைத் தேடுகிறது...",
        "nearest_hospitals": "<h3>📋 அருகிலுள்ள மருத்துவமனைகள்</h3>",
        "hospital_card": "<div class=\"hospital-card\"><div class=\"hospital-name\">{0}. {1}</div><div class=\"hospital-distance\">📍 {2} கி.மீ தொலைவில்</div><div class=\"hospital-actions\"><a href=\"{3}\" target=\"_blank\" class=\"primary-button\">📱 கூகுள் மேப்ஸ்</a><a href=\"{4}\" target=\"_blank\" class=\"secondary-button\">🗺️ OSM</a></div></div>",
        "no_hospitals_found": "😕 குறிப்பிட்ட ஆரத்திற்குள் மருத்துவமனைகள் எதுவும் கிடைக்கவில்லை. தேடல் தூரத்தை அதிகரிக்க முயற்சிக்கவும்.",
        "click_detect_location": "👆 உங்களுக்கு அருகில் உள்ள மருத்துவமனைகளைக் கண்டறிய 'எனது இருப்பிடத்தைக் கண்டறி' என்பதைக் கிளிக் செய்யவும்",
        "map_placeholder": "இருப்பிடக் கண்டறிதலுக்குப் பிறகு வரைபடம் இங்கே தோன்றும்",
        "location_error": "இருப்பிடத்தைக் கண்டறிய முடியவில்லை.",
        "fetch_hospitals_error": "மருத்துவமனைகளைப் பெற முடியவில்லை: {0}"
    },
    "hi": {
        "page_title": "आस-पास के अस्पताल",
        "page_icon": "🏥",
        "app_header": "<h1>🏥 आस-पास के अस्पताल</h1>",
        "app_description": "<div class=\"app-description\">अपने वर्तमान स्थान के पास अस्पतालों का पता लगाएं। यह ऐप OpenStreetMap डेटा का उपयोग करके आपके आसपास के चिकित्सा सुविधाओं का पता लगाती है और दूरी की जानकारी प्रदान करती है।</div>",
        "settings_panel": "⚙️ खोज सेटिंग्स",
        "search_radius": "खोज त्रिज्या (किमी)",
        "maximum_results": "अधिकतम परिणाम",
        "detect_location_button": "📍 मेरे स्थान का पता लगाएं",
        "refresh_button": "🔄 परिणाम रीफ्रेश करें",
        "detecting_location": "आपका स्थान पता लगा रहा है...",
        "your_location": "<strong>📍 आपका स्थान:</strong> {0:.6f}, {1:.6f}<br><small>{2} किमी त्रिज्या के भीतर अस्पतालों की खोज कर रहा है</small>",
        "searching_hospitals": "🔍 आस-पास के अस्पतालों की खोज कर रहा है...",
        "nearest_hospitals": "<h3>📋 निकटतम अस्पताल</h3>",
        "hospital_card": "<div class=\"hospital-card\"><div class=\"hospital-name\">{0}. {1}</div><div class=\"hospital-distance\">📍 {2} किमी दूर</div><div class=\"hospital-actions\"><a href=\"{3}\" target=\"_blank\" class=\"primary-button\">📱 गूगल मैप्स</a><a href=\"{4}\" target=\"_blank\" class=\"secondary-button\">🗺️ OSM</a></div></div>",
        "no_hospitals_found": "😕 निर्दिष्ट त्रिज्या के भीतर कोई अस्पताल नहीं मिला। खोज दूरी बढ़ाने का प्रयास करें।",
        "click_detect_location": "👆 अपने पास के अस्पतालों का पता लगाने के लिए 'मेरे स्थान का पता लगाएं' पर क्लिक करें",
        "map_placeholder": "स्थान का पता लगाने के बाद मानचित्र यहां दिखाई देगा",
        "location_error": "स्थान का पता नहीं लगा सका।",
        "fetch_hospitals_error": "अस्पतालों को प्राप्त करने में विफल: {0}"
    },
    "te": {
        "page_title": "సమీప ఆసుపత్రులు",
        "page_icon": "🏥",
        "app_header": "<h1>🏥 సమీప ఆసుపత్రులు</h1>",
        "app_description": "<div class=\"app-description\">మీ ప్రస్తుత స్థానానికి దగ్గరలో ఉన్న ఆసుపత్రులను కనుగొనండి. ఈ యాప్ OpenStreetMap డేటాను ఉపయోగించి మీ చుట్టూ ఉన్న వైద్య సౌకర్యాలను కనుగొని దూర సమాచారాన్ని అందిస్తుంది.</div>",
        "settings_panel": "⚙️ శోధన సెట్టింగ్‌లు",
        "search_radius": "శోధన వ్యాసార్ధం (కి.మీ)",
        "maximum_results": "గరిష్ట ఫలితాలు",
        "detect_location_button": "📍 నా స్థానాన్ని కనుగొనండి",
        "refresh_button": "🔄 ఫలితాలను రిఫ్రెష్ చేయండి",
        "detecting_location": "మీ స్థానాన్ని కనుగొంటోంది...",
        "your_location": "<strong>📍 మీ స్థానం:</strong> {0:.6f}, {1:.6f}<br><small>{2} కి.మీ వ్యాసార్ధంలో ఆసుపత్రులను శోధిస్తోంది</small>",
        "searching_hospitals": "🔍 సమీప ఆసుపత్రుల కోసం శోధిస్తోంది...",
        "nearest_hospitals": "<h3>📋 సమీప ఆసుపత్రులు</h3>",
        "hospital_card": "<div class=\"hospital-card\"><div class=\"hospital-name\">{0}. {1}</div><div class=\"hospital-distance\">📍 {2} కి.మీ దూరంలో</div><div class=\"hospital-actions\"><a href=\"{3}\" target=\"_blank\" class=\"primary-button\">📱 గూగుల్ మ్యాప్స్</a><a href=\"{4}\" target=\"_blank\" class=\"secondary-button\">🗺️ OSM</a></div></div>",
        "no_hospitals_found": "😕 పేర్కొన్న వ్యాసార్ధంలో ఆసుపత్రులు కనుగొనబడలేదు. శోధన దూరాన్ని పెంచడానికి ప్రయత్నించండి.",
        "click_detect_location": "👆 మీకు సమీపంలో ఉన్న ఆసుపత్రులను కనుగొనడానికి 'నా స్థానాన్ని కనుగొనండి' పై క్లిక్ చేయండి",
        "map_placeholder": "స్థాన గుర్తింపు తర్వాత మ్యాప్ ఇక్కడ కనిపిస్తుంది",
        "location_error": "స్థానాన్ని గుర్తించలేకపోయాము.",
        "fetch_hospitals_error": "ఆసుపత్రులను పొందడంలో విఫలమైంది: {0}"
    },
    "en": {
        "page_title": "Nearby Hospitals",
        "page_icon": "🏥",
        "app_header": "<h1>🏥 Nearby Hospitals</h1>",
        "app_description": "<div class=\"app-description\">Find hospitals near your current location. This app uses OpenStreetMap data to locate medical facilities around you and provides distance information.</div>",
        "settings_panel": "⚙️ Search Settings",
        "search_radius": "Search radius (km)",
        "maximum_results": "Maximum results",
        "detect_location_button": "📍 Detect My Location",
        "refresh_button": "🔄 Refresh Results",
        "detecting_location": "Detecting your location...",
        "your_location": "<strong>📍 Your Location:</strong> {0:.6f}, {1:.6f}<br><small>Searching for hospitals within {2} km radius</small>",
        "searching_hospitals": "🔍 Searching for nearby hospitals...",
        "nearest_hospitals": "<h3>📋 Nearest Hospitals</h3>",
        "hospital_card": "<div class=\"hospital-card\"><div class=\"hospital-name\">{0}. {1}</div><div class=\"hospital-distance\">📍 {2} km away</div><div class=\"hospital-actions\"><a href=\"{3}\" target=\"_blank\" class=\"primary-button\">📱 Google Maps</a><a href=\"{4}\" target=\"_blank\" class=\"secondary-button\">🗺️ OSM</a></div></div>",
        "no_hospitals_found": "😕 No hospitals found within the specified radius. Try increasing the search distance.",
        "click_detect_location": "👆 Click 'Detect My Location' to find hospitals near you",
        "map_placeholder": "Map will appear here after location detection",
        "location_error": "Couldn't detect location.",
        "fetch_hospitals_error": "Failed to fetch hospitals: {0}"
    }
}

# Initialize session state for language if not exists
if 'language' not in st.session_state:
    st.session_state.language = 'en'  # Default to English

def main():
    """Enhanced Nearby Hospitals App with Dark Mode and Language Support"""
    # Get current language
    current_lang = st.session_state.language
    ui = UI_TRANSLATIONS[current_lang]
    
    st.set_page_config(
        page_title=ui["page_title"],
        page_icon=ui["page_icon"],
        layout="wide",
    )
    
    # Add language selector to sidebar
    st.sidebar.image("firstaid.png", width=80)
    
    with st.sidebar:
        st.markdown("### 🌐 " + ("Language" if current_lang == "en" else "மொழி" if current_lang == "ta" else "भाषा" if current_lang == "hi" else "భాష"))
        
        with st.container(border=True):
            selected_language = st.selectbox(
                "Select your preferred language",
                options=list(LANGUAGES.keys()),
                format_func=lambda x: LANGUAGES[x],
                index=list(LANGUAGES.keys()).index(current_lang),
                key="language_selector"
            )
        
        # Update session state when language changes
        if selected_language != current_lang:
            st.session_state.language = selected_language
            st.rerun()  # Rerun the app to reflect language changes
        
        st.divider()
    
    # Apply dark mode styling
    st.markdown("""
    <style>
    /* Dark mode colors */
    :root {
        --background-color: #121212;
        --card-background: #1e1e1e;
        --primary-color: #3b82f6;
        --secondary-color: #374151;
        --text-color: #e2e8f0;
        --muted-text: #9ca3af;
        --accent-color: #3b82f6;
        --border-color: #2d3748;
        --hover-color: #2d3748;
    }
    
    /* Main styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
        background-color: var(--background-color);
        color: var(--text-color);
    }
    
    /* Override Streamlit's default white background */
    .stApp {
        background-color: var(--background-color);
    }
    
    /* Headers */
    h1, h2, h3 {
        color: var(--text-color);
        font-weight: 700;
        border-bottom: 2px solid var(--accent-color);
        padding-bottom: 0.5rem;
    }
    
    /* Location card */
    .location-card {
        background-color: #1a2234;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 20px;
        border-left: 5px solid var(--accent-color);
        color: var(--text-color);
    }
    
    /* Hospital cards */
    .hospital-card {
        background-color: var(--card-background);
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
        border: 1px solid var(--border-color);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
        transition: all 0.2s ease;
        color: var(--text-color);
    }
    
    .hospital-card:hover {
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.3);
        transform: translateY(-2px);
        background-color: var(--hover-color);
    }
    
    /* Hospital details */
    .hospital-name {
        font-weight: 600;
        color: var(--accent-color);
        font-size: 1.1rem;
        margin-bottom: 4px;
    }
    
    .hospital-distance {
        color: var(--muted-text);
    }
    
    .hospital-actions {
        margin-top: 8px;
    }
    
    /* Map container */
    .map-container {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
        border: 1px solid var(--border-color);
    }
    
    /* Loading animation */
    @keyframes pulse {
        0% { opacity: 0.6; }
        50% { opacity: 1; }
        100% { opacity: 0.6; }
    }
    
    .loading {
        animation: pulse 1.5s infinite;
        background-color: #1a2234;
        padding: 12px;
        border-radius: 8px;
        text-align: center;
        color: var(--text-color);
    }
    
    /* Settings panel */
    .settings-panel {
        background-color: var(--card-background);
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 20px;
        border: 1px solid var(--border-color);
    }
    /* Buttons */
    .primary-button {
        background-color: #1d4ed8; /* vivid indigo */
        color: #ffffff;
        padding: 10px 18px;
        border-radius: 8px;
        text-decoration: none;
        display: inline-block;
        margin-right: 10px;
        font-weight: 600;
        border: none;
        cursor: pointer;
        transition: background-color 0.2s ease, transform 0.1s ease;
    }
    
    .primary-button:hover {
        background-color: #1e40af; /* deeper indigo */
        transform: translateY(-1px);
    }
    
    .secondary-button {
        background-color: #f4f4f5; /* light neutral */
        color: #111827; /* dark text for readability */
        padding: 10px 18px;
        border-radius: 8px;
        text-decoration: none;
        display: inline-block;
        margin-right: 10px;
        font-weight: 600;
        border: 1px solid #d1d5db;
        cursor: pointer;
        transition: background-color 0.2s ease, transform 0.1s ease;
    }
    
    .secondary-button:hover {
        background-color: #e5e7eb; /* subtle hover effect */
        transform: translateY(-1px);
    }
    
    /* Override Streamlit components */
    .stTextInput, .stSelectbox, .stSlider {
        background-color: var(--card-background);
        color: var(--text-color);
    }
    
    .stExpander {
        background-color: var(--card-background);
        border: 1px solid var(--border-color);
    }
    
    /* Divider */
    hr {
        border-top: 1px solid var(--border-color);
    }
    
    /* Info/warning messages */
    .stAlert {
        background-color: var(--card-background);
        color: var(--text-color);
        border: 1px solid var(--border-color);
    }
    
    /* App description */
    .app-description {
        color: var(--muted-text);
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # App header - use translations
    st.markdown(ui["app_header"], unsafe_allow_html=True)
    st.markdown(ui["app_description"], unsafe_allow_html=True)
    
    # Settings panel - use translations
    with st.expander(ui["settings_panel"], expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            radius = st.slider(ui["search_radius"], min_value=1, max_value=20, value=5)
            
        with col2:
            max_results = st.slider(ui["maximum_results"], min_value=3, max_value=15, value=5)
            
    # Get user location
    if 'user_location' not in st.session_state:
        st.session_state.user_location = None
        st.session_state.hospitals = None
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button(ui["detect_location_button"], use_container_width=True, type="primary"):
            with st.spinner(ui["detecting_location"]):
                user_lat, user_lon = get_user_location(ui)
                if user_lat and user_lon:
                    st.session_state.user_location = (user_lat, user_lon)
                    st.rerun()
    
    with col2:
        if st.button(ui["refresh_button"], use_container_width=True, 
                    disabled=not st.session_state.user_location):
            st.session_state.hospitals = None
            st.rerun()
    
    # Display location and search for hospitals
    if st.session_state.user_location:
        user_lat, user_lon = st.session_state.user_location
        
        # Location card - use translations
        st.markdown(ui["your_location"].format(user_lat, user_lon, radius), unsafe_allow_html=True)
        
        # Get hospitals if not already in session
        if not st.session_state.hospitals:
            with st.spinner(ui["searching_hospitals"]):
                hospitals = get_nearby_hospitals_osm(user_lat, user_lon, 
                                                   radius=radius*1000, 
                                                   max_results=max_results,
                                                   ui=ui)
                
                # Add a small delay to show the loading effect
                time.sleep(0.5)
                st.session_state.hospitals = hospitals
        else:
            hospitals = st.session_state.hospitals
        
        # Display results in two columns
        if hospitals:
            col1, col2 = st.columns([3, 2])
            
            with col1:
                # Create a Folium map with a dark theme
                m = folium.Map(location=[user_lat, user_lon], zoom_start=13, 
                              tiles="CartoDB dark_matter")
                
                # Add user marker
                folium.Marker(
                    [user_lat, user_lon],
                    popup="Your Location",
                    icon=folium.Icon(color="blue", icon="user", prefix="fa"),
                ).add_to(m)
                
                # Add hospital markers
                for h in hospitals:
                    folium.Marker(
                        [h["lat"], h["lon"]],
                        popup=f"<b>{h['name']}</b><br>{h['distance_km']} km",
                        icon=folium.Icon(color="red", icon="plus", prefix="fa"),
                    ).add_to(m)
                
                # Add circle showing search radius
                folium.Circle(
                    radius=radius*1000,
                    location=[user_lat, user_lon],
                    color="#3b82f6",
                    fill=True,
                    fill_opacity=0.2,
                ).add_to(m)
                
                st.markdown("<div class='map-container'>", unsafe_allow_html=True)
                folium_static(m, width=700)
                st.markdown("</div>", unsafe_allow_html=True)
            
            with col2:
                st.markdown(ui["nearest_hospitals"], unsafe_allow_html=True)
                
                for i, h in enumerate(hospitals):
                    osm_url = f"https://www.openstreetmap.org/?mlat={h['lat']}&mlon={h['lon']}#map=16/{h['lat']}/{h['lon']}"
                    google_maps_url = f"https://www.google.com/maps/search/?api=1&query={h['lat']},{h['lon']}"
                    
                    # Use the hospital_card translation with formatting
                    st.markdown(ui["hospital_card"].format(
                        i+1, h['name'], h['distance_km'], google_maps_url, osm_url
                    ), unsafe_allow_html=True)
        else:
            st.warning(ui["no_hospitals_found"])
    else:
        # Show placeholder when no location detected
        st.info(ui["click_detect_location"])
        
        # Show example map as placeholder
        col1, col2 = st.columns([3, 2])
        with col1:
            st.markdown(f"<div class='loading'>{ui['map_placeholder']}</div>", 
                      unsafe_allow_html=True)
            
# 📍 Get user's location using IP (updated to use translations)
def get_user_location(ui):
    try:
        res = requests.get("https://ipinfo.io/json")
        if res.status_code == 200:
            data = res.json()
            loc = data["loc"].split(",")
            return float(loc[0]), float(loc[1])
    except:
        pass
    st.error(ui["location_error"])
    return None, None

# 🏥 Get nearby hospitals from OpenStreetMap (updated to use translations)
def get_nearby_hospitals_osm(lat, lon, radius=5000, max_results=5, ui=None):
    overpass_url = "http://overpass-api.de/api/interpreter"
    query = f"""
    [out:json];
    (
      node["amenity"="hospital"](around:{radius},{lat},{lon});
      way["amenity"="hospital"](around:{radius},{lat},{lon});
      relation["amenity"="hospital"](around:{radius},{lat},{lon});
    );
    out center;
    """

    try:
        res = requests.post(overpass_url, data=query)
        data = res.json()
        hospitals = []
        for element in data["elements"]:
            if "tags" in element:
                name = element["tags"].get("name", "Unnamed Hospital")
                h_lat = element.get("lat") or element["center"]["lat"]
                h_lon = element.get("lon") or element["center"]["lon"]
                distance = geodesic((lat, lon), (h_lat, h_lon)).km
                hospitals.append({
                    "name": name,
                    "lat": h_lat,
                    "lon": h_lon,
                    "distance_km": round(distance, 2)
                })

        # Sort by distance and return top results
        hospitals = sorted(hospitals, key=lambda x: x["distance_km"])[:max_results]
        return hospitals

    except Exception as e:
        if ui:
            st.error(ui["fetch_hospitals_error"].format(str(e)))
        else:
            st.error(f"Failed to fetch hospitals: {e}")
        return []

if __name__ == "__main__":
    main()