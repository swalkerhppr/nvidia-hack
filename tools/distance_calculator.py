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


def calculate_routing_cost(distance_km: float,
                          volume_kg: float,
                          capacity_kg: float,
                          is_perishable: bool = False) -> float:
    """
    Calculate routing cost score for a recipient match
    
    Lower scores are better. Factors in:
    - Distance (primary factor)
    - Perishability urgency (doubles distance cost for perishables)
    - Capacity utilization (penalty for poor utilization)
    
    Args:
        distance_km: Distance to recipient
        volume_kg: Volume of food to deliver
        capacity_kg: Recipient's available capacity
        is_perishable: Whether food is perishable (urgent)
    
    Returns:
        Cost score (lower is better)
    """
    # Base cost: distance
    distance_cost = distance_km
    
    # Perishable urgency: double the distance cost for perishables
    if is_perishable:
        distance_cost *= 2.0
    
    # Capacity utilization penalty
    # Prefer recipients who can use more of their capacity
    utilization = volume_kg / capacity_kg if capacity_kg > 0 else 0
    
    # Penalty for poor utilization (under 30% or over 90%)
    if utilization < 0.3:
        utilization_penalty = 5.0 * (0.3 - utilization)
    elif utilization > 0.9:
        utilization_penalty = 5.0 * (utilization - 0.9)
    else:
        utilization_penalty = 0
    
    total_cost = distance_cost + utilization_penalty
    
    return round(total_cost, 2)
