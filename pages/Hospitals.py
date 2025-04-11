import streamlit as st
import requests
from geopy.distance import geodesic
import time
import folium
from streamlit_folium import folium_static

def main():
    """Enhanced Nearby Hospitals App with Dark Mode"""
    st.set_page_config(
        page_title="Nearby Hospitals",
        page_icon="🏥",
        layout="wide",
    )
    
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
    
    # App header
    st.markdown("<h1>🏥 Nearby Hospitals</h1>", unsafe_allow_html=True)
    st.markdown("""
    <div class="app-description">
    Find hospitals near your current location. This app uses OpenStreetMap data to locate 
    medical facilities around you and provides distance information.
    </div>
    """, unsafe_allow_html=True)
    
    # Settings panel
    with st.expander("⚙️ Search Settings", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            radius = st.slider("Search radius (km)", min_value=1, max_value=20, value=5)
            
        with col2:
            max_results = st.slider("Maximum results", min_value=3, max_value=15, value=5)
            
    # Get user location
    if 'user_location' not in st.session_state:
        st.session_state.user_location = None
        st.session_state.hospitals = None
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("📍 Detect My Location", use_container_width=True, type="primary"):
            with st.spinner("Detecting your location..."):
                user_lat, user_lon = get_user_location()
                if user_lat and user_lon:
                    st.session_state.user_location = (user_lat, user_lon)
                    st.rerun()
    
    with col2:
        if st.button("🔄 Refresh Results", use_container_width=True, 
                    disabled=not st.session_state.user_location):
            st.session_state.hospitals = None
            st.rerun()
    
    # Display location and search for hospitals
    if st.session_state.user_location:
        user_lat, user_lon = st.session_state.user_location
        
        # Location card
        st.markdown(f"""
        <div class="location-card">
            <strong>📍 Your Location:</strong> {user_lat:.6f}, {user_lon:.6f}
            <br>
            <small>Searching for hospitals within {radius} km radius</small>
        </div>
        """, unsafe_allow_html=True)
        
        # Get hospitals if not already in session
        if not st.session_state.hospitals:
            with st.spinner("🔍 Searching for nearby hospitals..."):
                hospitals = get_nearby_hospitals_osm(user_lat, user_lon, 
                                                   radius=radius*1000, 
                                                   max_results=max_results)
                
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
                st.markdown("<h3>📋 Nearest Hospitals</h3>", unsafe_allow_html=True)
                
                for i, h in enumerate(hospitals):
                    osm_url = f"https://www.openstreetmap.org/?mlat={h['lat']}&mlon={h['lon']}#map=16/{h['lat']}/{h['lon']}"
                    google_maps_url = f"https://www.google.com/maps/search/?api=1&query={h['lat']},{h['lon']}"
                    
                    st.markdown(f"""
                    <div class="hospital-card">
                        <div class="hospital-name">
                            {i+1}. {h['name']}
                        </div>
                        <div class="hospital-distance">
                            📍 {h['distance_km']} km away
                        </div>
                        <div class="hospital-actions">
                            <a href="{google_maps_url}" target="_blank" class="primary-button">
                                📱 Google Maps
                            </a>
                            <a href="{osm_url}" target="_blank" class="secondary-button">
                                🗺️ OSM
                            </a>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("😕 No hospitals found within the specified radius. Try increasing the search distance.")
    else:
        # Show placeholder when no location detected
        st.info("👆 Click 'Detect My Location' to find hospitals near you")
        
        # Show example map as placeholder
        col1, col2 = st.columns([3, 2])
        with col1:
            st.markdown("<div class='loading'>Map will appear here after location detection</div>", 
                      unsafe_allow_html=True)
            
# 📍 Get user's location using IP (unchanged)
def get_user_location():
    try:
        res = requests.get("https://ipinfo.io/json")
        if res.status_code == 200:
            data = res.json()
            loc = data["loc"].split(",")
            return float(loc[0]), float(loc[1])
    except:
        pass
    st.error("Couldn't detect location.")
    return None, None

# 🏥 Get nearby hospitals from OpenStreetMap (unchanged)
def get_nearby_hospitals_osm(lat, lon, radius=5000, max_results=5):
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
        st.error(f"Failed to fetch hospitals: {e}")
        return []

if __name__ == "__main__":
    main()