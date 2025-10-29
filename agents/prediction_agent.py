"""
Prediction Agent - Analyzes events and predicts food surplus
"""
from typing import Dict, List
from .base_agent import BaseAgent
from tools import calculate_surplus_score, estimate_food_volume


class PredictionAgent(BaseAgent):
    """
    Autonomous agent that analyzes events and predicts surplus
    
    Uses Nemotron for reasoning + tool calls for quantification
    """
    
    def __init__(self):
        super().__init__("Prediction Agent")
        self.system_prompt = """You are a food waste prediction specialist for FeastGuard.AI.

Your role is to analyze event data and predict if food surplus will occur.

Consider these factors:
1. Attendee count (more people = more potential waste)
2. Catering type (buffet > family_style > plated)
3. Event duration (longer events = more waste)
4. Weather conditions (affects attendance and consumption)

Think step-by-step about surplus likelihood and provide your reasoning."""
    
    def analyze(self, event: dict) -> dict:
        """
        Analyze event and predict surplus
        
        Args:
            event: Event dictionary with attributes
            
        Returns:
            Prediction dict with surplus details and reasoning
        """
        # Step 1: Get Nemotron reasoning
        reasoning = self._reason_about_surplus(event)
        
        # Step 2: Calculate surplus score using tool
        surplus_score = calculate_surplus_score(event)
        
        # Step 3: Estimate volume and categorize using tool
        surplus_details = estimate_food_volume(event, surplus_score)
        
        # Step 4: Assess confidence
        confidence = self._assess_confidence(event, surplus_score)
        
        # Combine results
        prediction = {
            "event_id": event["event_id"],
            "event_name": event["name"],
            "has_surplus": surplus_details["category"] != "none",
            "predicted_kg": surplus_details["predicted_kg"],
            "category": surplus_details["category"],
            "urgency": surplus_details["urgency"],
            "surplus_score": surplus_score,
            "confidence": confidence,
            "reasoning": reasoning
        }
        
        return prediction
    
    def _reason_about_surplus(self, event: dict) -> str:
        """
        Use Nemotron to reason about surplus likelihood
        """
        user_prompt = f"""Analyze this event for food surplus potential:

Event: {event['name']}
- Attendees: {event['attendees']}
- Catering Type: {event['catering_type']}
- Duration: {event['duration_hours']} hours
- Weather: {event['weather']}
- Food Types: {', '.join(event['food_type'])}

Think through:
1. What factors suggest surplus might occur?
2. Is the food likely to be perishable or non-perishable?
3. What's the urgency level for redistribution?

Provide a brief 2-3 sentence analysis."""
        
        reasoning = self.think(self.system_prompt, user_prompt, temperature=0.7)
        return reasoning
    
    def _assess_confidence(self, event: dict, surplus_score: float) -> float:
        """
        Calculate confidence in prediction
        
        Higher confidence when:
        - Clear indicators (buffet, high attendance)
        - Score far from thresholds
        """
        # Base confidence on score distance from thresholds
        if surplus_score < 0.3:
            confidence = 0.6  # Low surplus, moderate confidence
        elif surplus_score < 0.6:
            confidence = 0.7  # Mid-range, decent confidence  
        else:
            confidence = 0.85  # High surplus, strong confidence
        
        # Boost for clear buffet events
        if event.get("catering_type") == "buffet" and event.get("attendees", 0) > 500:
            confidence = min(confidence + 0.1, 0.95)
        
        return round(confidence, 2)
    
    def format_log(self, prediction: dict) -> str:
        """Format prediction for logging"""
        emoji = "🔴" if prediction["urgency"] == "high" else "🟡" if prediction["urgency"] == "medium" else "🟢"
        
        if not prediction["has_surplus"]:
            return self.log(f"✅ {prediction['event_name']}: No significant surplus expected")
        
        return self.log(
            f"{emoji} {prediction['event_name']}: "
            f"{prediction['predicted_kg']}kg {prediction['category']} surplus predicted "
            f"(confidence: {prediction['confidence']:.0%})"
        )

