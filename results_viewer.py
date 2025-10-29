"""
FeastGuard.AI Results Viewer
Visualize multi-agent workflow results powered by NVIDIA Nemotron
"""
import streamlit as st
import folium
from streamlit_folium import st_folium
import json
from pathlib import Path
import pandas as pd
from datetime import datetime

# Page config
st.set_page_config(
    page_title="FeastGuard.AI - Results Viewer",
    page_icon="🍽️",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .stat-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
    }
    .stat-number {
        font-size: 2.5rem;
        font-weight: bold;
        color: #667eea;
    }
    .stat-label {
        font-size: 1rem;
        color: #666;
        margin-top: 0.5rem;
    }
    .message-card {
        background-color: #f8f9fa;
        border-left: 4px solid #667eea;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
    .reasoning-box {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
        font-style: italic;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_results():
    """Load results from JSON file"""
    results_file = Path("results.json")
    if results_file.exists():
        with open(results_file, 'r') as f:
            return json.load(f)
    return None

def create_map(routes):
    """Create Folium map with routes"""
    if not routes:
        return None
    
    # Center on Denver
    map_center = [39.7392, -104.9903]
    m = folium.Map(location=map_center, zoom_start=11)
    
    # Add routes
    for route in routes:
        if route.get('recipient_id'):  # Only show successful routes
            # Event marker (red)
            folium.Marker(
                location=route['event_location'],
                popup=f"<b>{route['event_name']}</b><br>{route['volume_kg']:.0f}kg surplus",
                icon=folium.Icon(color='red', icon='utensils', prefix='fa'),
                tooltip=route['event_name']
            ).add_to(m)
            
            # Recipient marker (green)
            folium.Marker(
                location=route['recipient_location'],
                popup=f"<b>{route['recipient_name']}</b><br>{route['distance_km']:.1f}km away",
                icon=folium.Icon(color='green', icon='home', prefix='fa'),
                tooltip=route['recipient_name']
            ).add_to(m)
            
            # Draw line between them
            folium.PolyLine(
                locations=[route['event_location'], route['recipient_location']],
                color='#667eea',
                weight=3,
                opacity=0.7,
                popup=f"{route['distance_km']:.1f}km"
            ).add_to(m)
    
    return m

def main():
    # Header
    st.markdown('<h1 class="main-header">🍽️ FeastGuard.AI Results</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666; font-size: 1.2rem;">Multi-Agent Food Redistribution powered by NVIDIA Nemotron</p>', unsafe_allow_html=True)
    
    # Load results
    results = load_results()
    
    if not results:
        st.error("❌ No results found. Please run `python main.py` first to generate results.")
        st.info("💡 The workflow will analyze events, find optimal routes, and generate outreach messages.")
        return
    
    predictions = results.get('predictions', [])
    routes = results.get('routes', [])
    messages = results.get('messages', [])
    
    # Calculate metrics
    successful_routes = [r for r in routes if r.get('recipient_id')]
    total_rescued = sum(r['volume_kg'] for r in successful_routes)
    events_with_surplus = len([p for p in predictions if p['has_surplus']])
    
    # Summary Stats
    st.markdown("## 📊 Workflow Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{len(predictions)}</div>
            <div class="stat-label">Events Processed</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{events_with_surplus}</div>
            <div class="stat-label">Surplus Detected</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{len(successful_routes)}</div>
            <div class="stat-label">Successful Routes</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{total_rescued:.0f}kg</div>
            <div class="stat-label">Food Rescued</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Map Visualization
    if successful_routes:
        st.markdown("## 🗺️ Route Visualization")
        st.markdown("*Red markers: Events with surplus • Green markers: Recipient organizations*")
        
        map_obj = create_map(routes)
        if map_obj:
            st_folium(map_obj, width=1200, height=500)
    
    st.markdown("---")
    
    # Tabs for detailed results
    tab1, tab2, tab3 = st.tabs(["🔍 Predictions", "🚚 Routes", "📧 Outreach Messages"])
    
    with tab1:
        st.markdown("## 🔍 AI Predictions")
        st.markdown("*Powered by NVIDIA Nemotron AI*")
        
        if not predictions:
            st.info("No predictions found.")
        
        for pred in predictions:
            if pred['has_surplus']:
                with st.expander(f"🔴 **{pred['event_name']}** - {pred['predicted_kg']:.0f}kg {pred['category']}", expanded=True):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"**Surplus Amount:** {pred['predicted_kg']:.2f}kg")
                        st.markdown(f"**Category:** {pred['category'].title()}")
                        st.markdown(f"**Urgency:** {pred['urgency'].upper()}")
                        st.markdown(f"**Confidence:** {pred['confidence']:.0%}")
                    
                    with col2:
                        urgency_color = {
                            'high': '🔴',
                            'medium': '🟡',
                            'low': '🟢'
                        }
                        st.markdown(f"### {urgency_color.get(pred['urgency'], '⚪')} Priority")
                    
                    st.markdown("**🤖 AI Reasoning:**")
                    st.markdown(f'<div class="reasoning-box">{pred["reasoning"]}</div>', unsafe_allow_html=True)
            else:
                with st.expander(f"✅ **{pred['event_name']}** - No significant surplus"):
                    st.markdown(f"**Confidence:** {pred['confidence']:.0%}")
                    st.markdown("**🤖 AI Reasoning:**")
                    st.markdown(f'<div class="reasoning-box">{pred["reasoning"]}</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown("## 🚚 Optimized Routes")
        st.markdown("*Intelligent matching powered by NVIDIA Nemotron*")
        
        if not successful_routes:
            st.warning("No successful routes found. Recipients may not have sufficient capacity.")
        
        for route in routes:
            if route.get('recipient_id'):
                with st.expander(f"🚚 **{route['event_name']}** → **{route['recipient_name']}**", expanded=True):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Distance", f"{route['distance_km']:.1f} km")
                    with col2:
                        st.metric("Volume", f"{route['volume_kg']:.0f} kg")
                    with col3:
                        st.metric("Food Type", route['food_category'].title())
                    
                    st.markdown("**🤖 AI Route Reasoning:**")
                    st.markdown(f'<div class="reasoning-box">{route["reasoning"]}</div>', unsafe_allow_html=True)
                    
                    if route.get('alternatives'):
                        st.markdown("**Alternative Recipients Considered:**")
                        for alt in route['alternatives']:
                            st.markdown(f"- {alt['name']} ({alt['distance_km']:.1f}km)")
            else:
                with st.expander(f"⚠️ **{route['event_name']}** - No suitable recipient found"):
                    st.markdown(f"**Reason:** {route['reasoning']}")
    
    with tab3:
        st.markdown("## 📧 AI-Generated Outreach Messages")
        st.markdown("*Professional communication crafted by NVIDIA Nemotron*")
        
        if not messages:
            st.info("No outreach messages generated (no successful routes).")
        
        for msg in messages:
            st.markdown(f"""
            <div class="message-card">
                <h3>📬 Message to {msg['recipient_name']}</h3>
                <p><strong>Event:</strong> {msg['event_name']}</p>
                <p><strong>Urgency:</strong> {msg['urgency_level'].upper()}</p>
                <p><strong>Volume:</strong> {msg['volume_kg']:.0f}kg {msg['food_category']}</p>
                <p><strong>Distance:</strong> {msg['distance_km']:.1f}km</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("**Message Content:**")
            st.info(msg['message_content'])
            
            st.markdown("**🤖 Communication Strategy:**")
            st.markdown(f'<div class="reasoning-box">{msg["strategy_reasoning"]}</div>', unsafe_allow_html=True)
            
            st.markdown(f"**Send Time:** {msg['estimated_send_time']}")
            st.markdown("---")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem;">
        <p><strong>FeastGuard.AI</strong> - Autonomous Food Redistribution System</p>
        <p>Powered by 🧠 <strong>NVIDIA Nemotron</strong> + ⚙️ <strong>LangGraph Multi-Agent System</strong></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

