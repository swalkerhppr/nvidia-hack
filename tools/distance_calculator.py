"""
Distance calculation tool functions
"""
import math
from typing import List, Tuple

def calculate_distance(loc1: Tuple[float, float], loc2: Tuple[float, float]) -> float:
    """
    Calculate distance between two lat/lon coordinates using Haversine formula
    
    Args:
        loc1: (latitude, longitude) tuple
        loc2: (latitude, longitude) tuple
    
    Returns:
        Distance in kilometers
    """
    lat1, lon1 = loc1
    lat2, lon2 = loc2
    
    # Haversine formula
    R = 6371  # Earth's radius in km
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    return round(distance, 2)


def get_distance_matrix(events: List[dict], recipients: List[dict]) -> dict:
    """
    Calculate distance matrix between all events and recipients
    
    Args:
        events: List of event dictionaries with location
        recipients: List of recipient dictionaries with location
    
    Returns:
        Dict mapping (event_id, recipient_id) to distance
    """
    distance_matrix = {}
    
    for event in events:
        event_loc = tuple(event.get("location", [0, 0]))
        
        for recipient in recipients:
            recipient_loc = tuple(recipient.get("location", [0, 0]))
            
            key = (event["event_id"], recipient["recipient_id"])
            distance_matrix[key] = calculate_distance(event_loc, recipient_loc)
    
    return distance_matrix


def find_nearby_recipients(event_location: Tuple[float, float], 
                          recipients: List[dict], 
                          max_distance_km: float = 10) -> List[dict]:
    """
    Find recipients within max distance of event
    
    Args:
        event_location: (lat, lon) tuple
        recipients: List of recipient dicts
        max_distance_km: Maximum distance threshold
    
    Returns:
        List of recipients within range, sorted by distance
    """
    nearby = []
    
    for recipient in recipients:
        recipient_loc = tuple(recipient.get("location", [0, 0]))
        distance = calculate_distance(event_location, recipient_loc)
        
        if distance <= max_distance_km:
            nearby.append({
                **recipient,
                "distance_km": distance
            })
    
    # Sort by distance
    nearby.sort(key=lambda x: x["distance_km"])
    
    return nearby

