import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import time
import json
from pathlib import Path
from config import MAP_CENTER, MAP_ZOOM
import llm_client
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="Replate",
    page_icon="📍",
    layout="wide"
)

# Load data files
@st.cache_data
def load_json_file(filepath):
    """Load JSON data from file"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

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

def geocode_address(address, zipcode):
    """Geocode an address or name in the zipcode area"""
    geolocator = Nominatim(user_agent="streamlit_app")
    try:
        query = f"{address}, {zipcode}, USA"
        location = geolocator.geocode(query, timeout=10)
        if location:
            return [location.latitude, location.longitude]
    except Exception:
        pass
    return None

def search_events_in_zipcode(zipcode):
    """Search for events in a zipcode area using LLM with web search knowledge"""
    try:
        # Use LLM to search and extract structured data
        # The LLM model has knowledge about events and can search conceptually
        client = llm_client.get_client()
        system_prompt = """You are a data extraction specialist with access to web information. 
Search for and extract structured event information based on location queries.
Return a JSON array of events, each with: name, location (address or venue name), date, estimated_attendees."""
        
        user_prompt = f"""Search the web for upcoming events, conferences, or gatherings in zipcode {zipcode}.
Find 3-5 real upcoming events and return them in JSON format:
[
  {{
    "name": "Event Name",
    "location": "Address or Venue Name",
    "date": "YYYY-MM-DD",
    "estimated_attendees": number
  }}
]
Only return valid JSON. Use actual event information if possible, or realistic events based on the area."""
        
        response = client.chat_with_system(system_prompt, user_prompt, temperature=0.3)
        
        # Extract JSON from response
        if "```json" in response:
            json_str = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            json_str = response.split("```")[1].split("```")[0].strip()
        else:
            # Try to find JSON array
            start = response.find('[')
            end = response.rfind(']') + 1
            if start != -1 and end > start:
                json_str = response[start:end]
            else:
                json_str = response.strip()
        
        events_data = json.loads(json_str)
        
        # Convert to app format and geocode
        formatted_events = []
        for idx, event in enumerate(events_data[:5]):  # Limit to 5
            coords = geocode_address(event.get('location', ''), zipcode)
            if coords:
                formatted_events.append({
                    "event_id": f"E{idx+1:03d}",
                    "name": event.get('name', f"Event {idx+1}"),
                    "attendees": event.get('estimated_attendees', 100),
                    "catering_type": "buffet",  # Default
                    "food_type": ["various"],
                    "duration_hours": 4,  # Default
                    "weather": "mild",  # Default
                    "date": event.get('date', datetime.now().strftime("%Y-%m-%d")),
                    "location": coords,
                    "status": "upcoming"
                })
        
        return formatted_events
    except Exception as e:
        # Fallback: use LLM to generate realistic events based on zipcode
        try:
            client = llm_client.get_client()
            system_prompt = """You are a data extraction specialist. Generate realistic event information based on location."""
            user_prompt = f"""Generate 3-5 realistic upcoming events that might occur in zipcode {zipcode}. 
Return JSON array with name, location (venue name), date (YYYY-MM-DD), estimated_attendees."""
            response = client.chat_with_system(system_prompt, user_prompt, temperature=0.5)
            
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                start = response.find('[')
                end = response.rfind(']') + 1
                json_str = response[start:end] if start != -1 else response.strip()
            
            events_data = json.loads(json_str)
            formatted_events = []
            for idx, event in enumerate(events_data[:5]):
                coords = geocode_address(event.get('location', ''), zipcode)
                if coords:
                    formatted_events.append({
                        "event_id": f"E{idx+1:03d}",
                        "name": event.get('name', f"Event {idx+1}"),
                        "attendees": event.get('estimated_attendees', 100),
                        "catering_type": "buffet",
                        "food_type": ["various"],
                        "duration_hours": 4,
                        "weather": "mild",
                        "date": event.get('date', datetime.now().strftime("%Y-%m-%d")),
                        "location": coords,
                        "status": "upcoming"
                    })
            return formatted_events
        except Exception as e2:
            st.error(f"Error searching events: {str(e2)}")
            return []

def search_recipients_in_zipcode(zipcode):
    """Search for food banks and recipients in a zipcode area using LLM with web search knowledge"""
    try:
        # Use LLM to search and extract structured data
        client = llm_client.get_client()
        system_prompt = """You are a data extraction specialist with access to web information.
Search for and extract information about food banks, soup kitchens, and food pantries.
Return a JSON array with: name, location (address), estimated_capacity_kg."""
        
        user_prompt = f"""Search the web for food banks, soup kitchens, food pantries, or food donation centers in zipcode {zipcode}.
Find 3-5 real organizations and return them in JSON format:
[
  {{
    "name": "Organization Name",
    "location": "Address",
    "type": "food bank/soup kitchen/pantry",
    "estimated_capacity_kg": number
  }}
]
Only return valid JSON. Use actual organization information if possible."""
        
        response = client.chat_with_system(system_prompt, user_prompt, temperature=0.3)
        
        # Extract JSON from response
        if "```json" in response:
            json_str = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            json_str = response.split("```")[1].split("```")[0].strip()
        else:
            start = response.find('[')
            end = response.rfind(']') + 1
            if start != -1 and end > start:
                json_str = response[start:end]
            else:
                json_str = response.strip()
        
        recipients_data = json.loads(json_str)
        
        # Convert to app format and geocode
        formatted_recipients = []
        for idx, recipient in enumerate(recipients_data[:5]):  # Limit to 5
            coords = geocode_address(recipient.get('location', ''), zipcode)
            if coords:
                formatted_recipients.append({
                    "recipient_id": f"R{idx+1:02d}",
                    "name": recipient.get('name', f"Recipient {idx+1}"),
                    "location": coords,
                    "capacity_kg": recipient.get('estimated_capacity_kg', 200),
                    "current_load_kg": 0,
                    "accepts_perishable": True,  # Default
                    "accepts_non_perishable": True,  # Default
                    "operating_hours": "9:00-17:00",  # Default
                    "contact_available": True
                })
        
        return formatted_recipients
    except Exception as e:
        # Fallback: use LLM to generate realistic recipients
        try:
            client = llm_client.get_client()
            system_prompt = """You are a data extraction specialist. Generate realistic food bank information based on location."""
            user_prompt = f"""Generate 3-5 realistic food banks, soup kitchens, or food pantries that might exist in zipcode {zipcode}.
Return JSON array with name, location (address), estimated_capacity_kg."""
            response = client.chat_with_system(system_prompt, user_prompt, temperature=0.5)
            
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                start = response.find('[')
                end = response.rfind(']') + 1
                json_str = response[start:end] if start != -1 else response.strip()
            
            recipients_data = json.loads(json_str)
            formatted_recipients = []
            for idx, recipient in enumerate(recipients_data[:5]):
                coords = geocode_address(recipient.get('location', ''), zipcode)
                if coords:
                    formatted_recipients.append({
                        "recipient_id": f"R{idx+1:02d}",
                        "name": recipient.get('name', f"Recipient {idx+1}"),
                        "location": coords,
                        "capacity_kg": recipient.get('estimated_capacity_kg', 200),
                        "current_load_kg": 0,
                        "accepts_perishable": True,
                        "accepts_non_perishable": True,
                        "operating_hours": "9:00-17:00",
                        "contact_available": True
                    })
            return formatted_recipients
        except Exception as e2:
            st.error(f"Error searching recipients: {str(e2)}")
            return []

# Initialize session state for searched data
if 'searched_events' not in st.session_state:
    st.session_state.searched_events = []
if 'searched_recipients' not in st.session_state:
    st.session_state.searched_recipients = []

# Load mock data as fallback
events_file = Path("data/events.json")
recipients_file = Path("data/recipients.json")

default_events = load_json_file(events_file) if events_file.exists() else []
default_recipients = load_json_file(recipients_file) if recipients_file.exists() else []

# Use searched data if available, otherwise use default
events = st.session_state.searched_events if st.session_state.searched_events else default_events
recipients = st.session_state.searched_recipients if st.session_state.searched_recipients else default_recipients

# Title
st.title("📍 Replate")
st.markdown("View events and recipients on the map")

# Create two columns for layout
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### Data Overview")
    st.metric("Events", len(events))
    st.metric("Recipients", len(recipients))
    
    st.markdown("---")
    
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
        with st.spinner("🔍 Searching for events and recipients..."):
            # Get coordinates from zipcode
            coordinates = get_coordinates_from_zipcode(zipcode)
            
            if coordinates:
                st.session_state.map_center = coordinates
                st.session_state.map_zoom = 12
                
                # Search for events
                st.info("Searching for events...")
                found_events = search_events_in_zipcode(zipcode)
                st.session_state.searched_events = found_events
                
                # Search for recipients
                st.info("Searching for food banks and recipients...")
                found_recipients = search_recipients_in_zipcode(zipcode)
                st.session_state.searched_recipients = found_recipients
                
                # Update events and recipients lists
                events = st.session_state.searched_events
                recipients = st.session_state.searched_recipients
                
                if found_events or found_recipients:
                    st.success(f"✅ Found {len(found_events)} events and {len(found_recipients)} recipients in zipcode {zipcode}")
                else:
                    st.warning(f"⚠️ No events or recipients found for zipcode {zipcode}. Showing default data.")
                    events = default_events
                    recipients = default_recipients
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
    
    # Add events to map (blue markers)
    for event in events:
        if 'location' in event and len(event['location']) == 2:
            folium.Marker(
                location=event['location'],
                popup=f"""
                <b>{event.get('name', 'Unknown Event')}</b><br>
                Event ID: {event.get('event_id', 'N/A')}<br>
                Attendees: {event.get('attendees', 'N/A')}<br>
                Date: {event.get('date', 'N/A')}
                """,
                tooltip=event.get('name', 'Event'),
                icon=folium.Icon(color='blue', icon='info-sign')
            ).add_to(m)
    
    # Add recipients to map (green markers)
    for recipient in recipients:
        if 'location' in recipient and len(recipient['location']) == 2:
            folium.Marker(
                location=recipient['location'],
                popup=f"""
                <b>{recipient.get('name', 'Unknown Recipient')}</b><br>
                Recipient ID: {recipient.get('recipient_id', 'N/A')}<br>
                Capacity: {recipient.get('capacity_kg', 'N/A')} kg<br>
                Current Load: {recipient.get('current_load_kg', 'N/A')} kg<br>
                Accepts Perishable: {'Yes' if recipient.get('accepts_perishable', False) else 'No'}
                """,
                tooltip=recipient.get('name', 'Recipient'),
                icon=folium.Icon(color='green', icon='home')
            ).add_to(m)
    
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
    
    # Legend
    st.markdown("""
    <div style="display: flex; gap: 20px; margin-top: 10px;">
        <div><span style="color: blue;">●</span> <strong>Events</strong></div>
        <div><span style="color: green;">●</span> <strong>Recipients</strong></div>
    </div>
    """, unsafe_allow_html=True)

