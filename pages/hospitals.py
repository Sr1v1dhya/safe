import streamlit as st
import requests
from geopy.distance import geodesic
import streamlit as st
st.set_page_config(page_title="Nearby Hospitals", page_icon="🏥")


# 📍 Get user's location using IP
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

# 🏥 Get real hospitals from OpenStreetMap Overpass API
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

        # ✅ Sort by distance and return top 5
        hospitals = sorted(hospitals, key=lambda x: x["distance_km"])[:max_results]
        return hospitals

    except Exception as e:
        st.error(f"Failed to fetch hospitals: {e}")
        return []

# 🚀 Main Streamlit App
st.title("🏥 Real Nearby Hospitals - OSM Edition")

user_lat, user_lon = get_user_location()

if user_lat and user_lon:
    st.success(f"📍 Your Location: {user_lat}, {user_lon}")
    st.write("🔍 Searching for hospitals within 5 km...")

    hospitals = get_nearby_hospitals_osm(user_lat, user_lon)

    if hospitals:
        # 📌 Display map
        st.map({
            "lat": [h["lat"] for h in hospitals],
            "lon": [h["lon"] for h in hospitals]
        })

        # 📋 Display hospital list with clickable map links
        st.subheader("Top 5 Nearest Hospitals")
        for h in hospitals:
            osm_url = f"https://www.openstreetmap.org/?mlat={h['lat']}&mlon={h['lon']}#map=16/{h['lat']}/{h['lon']}"
            st.markdown(
                f"🔹 **[{h['name']}]({osm_url})** — {h['distance_km']} km away",
                unsafe_allow_html=True
            )
    else:
        st.warning("No hospitals found nearby 🥺")
else:
    st.error("Location detection failed.")
