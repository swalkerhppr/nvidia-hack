import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import time
from config import MAP_CENTER, MAP_ZOOM

# Set page config
st.set_page_config(
    page_title="Replate",
    page_icon="📍",
    layout="wide"
)

# Initialize geocoder
@st.cache_data
def get_coordinates_from_zipcode(zipcode):
    """Get coordinates from a zipcode"""
    geolocator = Nominatim(user_agent="streamlit_app")
    try:
        location = geolocator.geocode(f"{zipcode}, USA", timeout=10)
        if location:
            return [location.latitude, location.longitude]
    except (GeocoderTimedOut, GeocoderUnavailable) as e:
        st.error(f"Geocoding error: {str(e)}")
        return None
    return None

# Title
st.title("📍 Zipcode Map Viewer")
st.markdown("Enter a zipcode and click the button to view it on the map")

# Create two columns for layout
col1, col2 = st.columns([1, 2])

with col1:
    # Text input for zipcode
    zipcode = st.text_input(
        "Enter Zipcode:",
        value="",
        placeholder="e.g., 80202",
        key="zipcode_input"
    )
    
    # Button
    button_clicked = st.button(
        "Make an impact",
        type="primary",
        use_container_width=True
    )

# Initialize session state for map center
if 'map_center' not in st.session_state:
    st.session_state.map_center = MAP_CENTER

if 'map_zoom' not in st.session_state:
    st.session_state.map_zoom = MAP_ZOOM

# Handle button click
if button_clicked:
    if zipcode:
        # Get coordinates from zipcode
        coordinates = get_coordinates_from_zipcode(zipcode)
        
        if coordinates:
            st.session_state.map_center = coordinates
            st.session_state.map_zoom = 12
            st.success(f"📍 Found location for zipcode {zipcode}")
        else:
            st.error(f"❌ Could not find location for zipcode: {zipcode}")
            st.info("Using default map center")
    else:
        st.warning("⚠️ Please enter a zipcode")

# Create map
with col2:
    st.subheader("Map View")
    
    # Create Folium map
    m = folium.Map(
        location=st.session_state.map_center,
        zoom_start=st.session_state.map_zoom,
        tiles='OpenStreetMap'
    )
    
    # Add marker if we have a zipcode
    if zipcode and button_clicked:
        if st.session_state.map_center != MAP_CENTER:
            folium.Marker(
                location=st.session_state.map_center,
                popup=f"Zipcode: {zipcode}",
                tooltip=f"Zipcode: {zipcode}",
                icon=folium.Icon(color='red', icon='info-sign')
            ).add_to(m)
    
    # Display map
    st_folium(m, width=700, height=500)

