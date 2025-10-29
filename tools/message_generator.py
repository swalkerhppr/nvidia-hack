"""
Message generation tool (Nemotron integration)
"""
import os
import requests
from typing import Optional
import config

def generate_outreach_message(recipient_name: str,
                              event_name: str,
                              food_details: dict,
                              urgency: str = "medium",
                              use_nemotron: bool = True) -> str:
    """
    Generate outreach message for coordination
    
    Args:
        recipient_name: Name of recipient organization
        event_name: Name of event with surplus
        food_details: Dict with category, volume_kg, pickup_time
        urgency: 'low', 'medium', or 'high'
        use_nemotron: Whether to use Nemotron API (fallback to template)
    
    Returns:
        Generated message string
    """
    volume = food_details.get("volume_kg", 0)
    category = food_details.get("category", "unknown")
    pickup_time = food_details.get("pickup_time", "end of event")
    
    if use_nemotron and os.getenv("NVIDIA_API_KEY"):
        return _generate_with_nemotron(
            recipient_name, event_name, volume, category, pickup_time, urgency
        )
    else:
        return _generate_template_message(
            recipient_name, event_name, volume, category, pickup_time, urgency
        )


def _generate_with_nemotron(recipient_name: str, event_name: str, 
                           volume: float, category: str, 
                           pickup_time: str, urgency: str) -> str:
    """
    Generate message using NVIDIA Nemotron via NVIDIA API
    """
    api_key = config.NVIDIA_API_KEY
    
    urgency_context = {
        "high": "This is time-sensitive perishable food that must be picked up within 2 hours.",
        "medium": "Please confirm availability for pickup today.",
        "low": "This is non-perishable food with flexible pickup timing."
    }
    
    prompt = f"""You are FeastGuard.AI, an autonomous food redistribution coordinator.

Generate a professional, warm outreach message to coordinate food donation pickup.

Details:
- Recipient: {recipient_name}
- Event: {event_name}
- Food Volume: {volume}kg
- Food Type: {category}
- Pickup Time: {pickup_time}
- Urgency: {urgency_context.get(urgency, '')}

The message should:
1. Be professional but friendly
2. Clearly state the opportunity
3. Include key logistics (volume, timing, food type)
4. Include a call-to-action
5. Be concise (3-4 sentences)

Generate only the message text, no subject line or signatures."""

    try:
        response = requests.post(
            config.NVIDIA_ENDPOINT,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": config.NEMOTRON_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 300,
                "stream": False
            },
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        else:
            # Fallback to template
            return _generate_template_message(
                recipient_name, event_name, volume, category, pickup_time, urgency
            )
    except Exception as e:
        print(f"Nemotron API error: {e}")
        return _generate_template_message(
            recipient_name, event_name, volume, category, pickup_time, urgency
        )


def _generate_template_message(recipient_name: str, event_name: str,
                               volume: float, category: str,
                               pickup_time: str, urgency: str) -> str:
    """
    Template-based message generation (fallback)
    """
    urgency_phrases = {
        "high": "We have time-sensitive perishable food available",
        "medium": "We have fresh food available",
        "low": "We have surplus food available"
    }
    
    intro = urgency_phrases.get(urgency, "We have surplus food available")
    
    message = f"""Hello {recipient_name},

{intro} from {event_name} that would be perfect for your organization. We have approximately {volume}kg of {category} food ready for pickup at {pickup_time}.

This is an excellent opportunity to provide fresh meals to those you serve. Can you confirm your availability for pickup?

Please respond at your earliest convenience. Thank you for your partnership in reducing food waste!

Best regards,
FeastGuard.AI Coordination System"""
    
    return message

