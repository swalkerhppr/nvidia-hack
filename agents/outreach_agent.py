"""
Outreach Agent - Generates coordination messages
"""
from typing import Dict, Optional
from .base_agent import BaseAgent
from tools import generate_outreach_message


class OutreachAgent(BaseAgent):
    """
    Autonomous agent that generates context-aware outreach messages
    
    Uses Nemotron for human-like, professional communication
    """
    
    def __init__(self):
        super().__init__("Outreach Agent")
        self.system_prompt = """You are a communication specialist for FeastGuard.AI.

Your role is to draft professional, warm outreach messages for food donation coordination.

Message guidelines:
1. Professional but friendly tone
2. Clear call-to-action
3. Include key logistics (volume, timing, food type)
4. Emphasize urgency appropriately
5. Be concise (3-4 sentences)

Adapt tone based on urgency:
- HIGH urgency: Direct, time-sensitive language
- MEDIUM urgency: Professional with gentle urgency
- LOW urgency: Relaxed, opportunity-focused"""
    
    def generate_message(self, route: dict) -> Optional[dict]:
        """
        Generate outreach message for confirmed route
        
        Args:
            route: Route dict from RoutingAgent
            
        Returns:
            Message dict with content and metadata, or None if no recipient
        """
        # Skip if no match
        if route["recipient_id"] is None:
            return None
        
        # Step 1: Prepare context for message generation
        food_details = {
            "volume_kg": route["volume_kg"],
            "category": route["food_category"],
            "pickup_time": self._estimate_pickup_time(route["urgency"])
        }
        
        # Step 2: Generate message using tool (which uses Nemotron)
        message_content = generate_outreach_message(
            recipient_name=route["recipient_name"],
            event_name=route["event_name"],
            food_details=food_details,
            urgency=route["urgency"],
            use_nemotron=True
        )
        
        # Step 3: Add strategic reasoning
        strategy = self._explain_strategy(route, message_content)
        
        # Step 4: Create message record
        message = {
            "recipient_id": route["recipient_id"],
            "recipient_name": route["recipient_name"],
            "event_id": route["event_id"],
            "event_name": route["event_name"],
            "message_content": message_content,
            "urgency_level": route["urgency"],
            "volume_kg": route["volume_kg"],
            "food_category": route["food_category"],
            "distance_km": route["distance_km"],
            "strategy_reasoning": strategy,
            "estimated_send_time": "immediate" if route["urgency"] == "high" else "within 1 hour"
        }
        
        return message
    
    def _estimate_pickup_time(self, urgency: str) -> str:
        """Estimate pickup window based on urgency"""
        if urgency == "high":
            return "within 2 hours (perishable)"
        elif urgency == "medium":
            return "today, before evening"
        else:
            return "flexible scheduling available"
    
    def _explain_strategy(self, route: dict, message: str) -> str:
        """
        Use Nemotron to explain communication strategy
        """
        user_prompt = f"""Analyze this outreach message strategy:

Context:
- Recipient: {route['recipient_name']}
- Food: {route['volume_kg']}kg {route['food_category']}
- Distance: {route['distance_km']:.1f}km
- Urgency: {route['urgency']}

Message Preview:
{message[:150]}...

In one sentence, explain the communication strategy and tone used."""
        
        reasoning = self.think(self.system_prompt, user_prompt, temperature=0.6)
        return reasoning
    
    def format_log(self, message: dict) -> str:
        """Format message for logging"""
        emoji = "🚨" if message["urgency_level"] == "high" else "📧"
        
        return self.log(
            f"{emoji} Message for {message['recipient_name']}: "
            f"{message['volume_kg']}kg {message['food_category']} "
            f"(send: {message['estimated_send_time']})"
        )
    
    def format_message_for_display(self, message: dict) -> str:
        """
        Format complete message for display/output
        """
        header = f"""
{'='*60}
OUTREACH MESSAGE
{'='*60}
To: {message['recipient_name']}
Re: {message['event_name']} - Food Donation Opportunity
Priority: {message['urgency_level'].upper()}
Volume: {message['volume_kg']}kg {message['food_category']}
Distance: {message['distance_km']:.1f}km
{'='*60}
"""
        
        footer = f"""
{'='*60}
Strategy: {message['strategy_reasoning']}
Send Time: {message['estimated_send_time']}
{'='*60}
"""
        
        return header + "\n" + message['message_content'] + "\n" + footer

