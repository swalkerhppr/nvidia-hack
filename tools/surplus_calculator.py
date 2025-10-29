"""
Surplus prediction tool functions
"""
import config

def calculate_surplus_score(event: dict) -> float:
    """
    Calculate surplus probability score based on event attributes
    
    Args:
        event: Event dictionary with attendees, duration, catering_type, weather
    
    Returns:
        Float between 0-1 indicating surplus likelihood
    """
    attendees = event.get("attendees", 0)
    duration_hours = event.get("duration_hours", 0)
    catering_type = event.get("catering_type", "plated")
    weather = event.get("weather", "mild")
    
    # Apply formula from README
    attendees_score = config.SURPLUS_WEIGHTS["attendees"] * (attendees / 1000)
    duration_score = config.SURPLUS_WEIGHTS["duration"] * (duration_hours / 5)
    catering_factor = config.CATERING_FACTORS.get(catering_type, 0.5)
    catering_score = config.SURPLUS_WEIGHTS["catering_factor"] * catering_factor
    weather_factor = config.WEATHER_FACTORS.get(weather, 0.0)
    weather_score = config.SURPLUS_WEIGHTS["weather_factor"] * weather_factor
    
    total_score = attendees_score + duration_score + catering_score - weather_score
    
    # Normalize to 0-1
    return min(max(total_score, 0.0), 1.0)


def estimate_food_volume(event: dict, surplus_score: float) -> dict:
    """
    Estimate food volume and categorize surplus type
    
    Args:
        event: Event dictionary
        surplus_score: Calculated surplus score
    
    Returns:
        Dict with predicted_kg, category, urgency
    """
    attendees = event.get("attendees", 0)
    
    # Rough estimate: 0.5kg per attendee for full catering
    base_volume = (attendees * 0.5) * surplus_score
    
    # Categorize
    category = "none"
    urgency = "low"
    
    for cat, (low, high) in config.SURPLUS_THRESHOLDS.items():
        if low <= surplus_score < high:
            category = cat
            break
    
    if category == "perishable":
        urgency = "high"
    elif category == "non_perishable":
        urgency = "medium"
    
    return {
        "predicted_kg": round(base_volume, 2),
        "category": category,
        "urgency": urgency,
        "score": round(surplus_score, 3)
    }


def get_weather_context(location: str, date: str) -> str:
    """
    Mock function to get weather context
    In production, this would call a weather API
    """
    # Mock weather data
    import random
    weathers = ["mild", "hot", "cold", "rainy"]
    return random.choice(weathers)

