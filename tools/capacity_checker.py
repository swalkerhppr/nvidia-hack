"""
Recipient capacity checking tool functions
"""
from typing import List
import config

def check_recipient_capacity(recipient: dict, volume_kg: float) -> dict:
    """
    Check if recipient can accept the food volume
    
    Args:
        recipient: Recipient dictionary with capacity_kg
        volume_kg: Volume of food to donate
    
    Returns:
        Dict with can_accept (bool), remaining_capacity, utilization_pct
    """
    capacity = recipient.get("capacity_kg", 0)
    current_load = recipient.get("current_load_kg", 0)
    
    available = capacity - current_load
    can_accept = available >= volume_kg
    
    utilization = ((current_load + volume_kg) / capacity * 100) if capacity > 0 else 0
    
    return {
        "can_accept": can_accept,
        "available_capacity_kg": round(available, 2),
        "utilization_pct": round(utilization, 1),
        "would_exceed": not can_accept
    }


def get_available_recipients(recipients: List[dict], 
                            food_category: str,
                            min_capacity_kg: float = 0) -> List[dict]:
    """
    Filter recipients by food type acceptance and capacity
    
    Args:
        recipients: List of recipient dictionaries
        food_category: 'perishable' or 'non_perishable'
        min_capacity_kg: Minimum capacity requirement
    
    Returns:
        Filtered list of available recipients
    """
    available = []
    
    for recipient in recipients:
        # Check food type acceptance
        if food_category == "perishable":
            accepts = recipient.get("accepts_perishable", False)
        elif food_category == "non_perishable":
            accepts = recipient.get("accepts_non_perishable", False)
        else:
            accepts = True  # Unknown category, accept by default
        
        if not accepts:
            continue
        
        # Check capacity
        capacity = recipient.get("capacity_kg", 0)
        current_load = recipient.get("current_load_kg", 0)
        available_capacity = capacity - current_load
        
        if available_capacity >= min_capacity_kg:
            available.append({
                **recipient,
                "available_capacity_kg": round(available_capacity, 2)
            })
    
    return available


def calculate_routing_cost(distance_km: float, 
                          volume_kg: float, 
                          capacity_kg: float,
                          is_perishable: bool) -> float:
    """
    Calculate routing cost for optimization
    
    Lower cost = better match
    
    Args:
        distance_km: Distance to recipient
        volume_kg: Food volume
        capacity_kg: Recipient capacity
        is_perishable: Whether food is perishable
    
    Returns:
        Cost score (lower is better)
    """
    # Distance penalty
    distance_weight = 2.0 if is_perishable else 1.0
    distance_cost = distance_km * distance_weight
    
    # Capacity utilization bonus (prefer fuller utilization)
    utilization = volume_kg / capacity_kg if capacity_kg > 0 else 0
    utilization_bonus = (1.0 - utilization) * 5  # Penalty for underutilization
    
    total_cost = distance_cost + utilization_bonus
    
    return round(total_cost, 2)

