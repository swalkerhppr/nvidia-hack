"""
Routing Agent - Optimizes surplus-to-recipient matching
"""
from typing import Dict, List, Optional
from .base_agent import BaseAgent
from tools import (
    get_available_recipients, 
    calculate_distance, 
    check_recipient_capacity,
    calculate_routing_cost
)


class RoutingAgent(BaseAgent):
    """
    Autonomous agent that optimizes food redistribution routing
    
    Uses Nemotron for strategic reasoning + tools for cost calculation
    """
    
    def __init__(self):
        super().__init__("Routing Agent")
        self.system_prompt = """You are a logistics optimization specialist for FeastGuard.AI.

Your role is to match food surplus with the best recipient organization.

Optimization priorities:
1. URGENCY: Perishable food needs pickup within 2 hours, prioritize nearby recipients
2. CAPACITY: Ensure recipient has space and accepts food type
3. DISTANCE: Minimize travel distance (especially for perishables)
4. UTILIZATION: Prefer recipients who can use most of the volume

Think strategically about the best match."""
    
    def find_route(self, 
                   prediction: dict, 
                   event: dict, 
                   recipients: List[dict]) -> Optional[dict]:
        """
        Find optimal recipient for predicted surplus
        
        Args:
            prediction: Prediction dict from PredictionAgent
            event: Original event dict with location
            recipients: List of available recipient orgs
            
        Returns:
            Route dict with assignment, or None if no match
        """
        # Skip if no surplus
        if not prediction["has_surplus"] or prediction["predicted_kg"] <= 0:
            return None
        
        # Step 1: Filter available recipients
        food_category = prediction["category"]
        available = get_available_recipients(
            recipients, 
            food_category=food_category,
            min_capacity_kg=prediction["predicted_kg"] * 0.5  # Need at least 50% capacity
        )
        
        if not available:
            return self._create_no_match_result(prediction, "No recipients available")
        
        # Step 2: Calculate costs for each candidate
        candidates = self._score_candidates(
            event=event,
            prediction=prediction,
            available_recipients=available
        )
        
        if not candidates:
            return self._create_no_match_result(prediction, "No suitable candidates")
        
        # Step 3: Get Nemotron reasoning for top candidate
        best_candidate = candidates[0]
        reasoning = self._reason_about_route(prediction, event, best_candidate, candidates[1:3])
        
        # Step 4: Create route assignment
        route = {
            "event_id": prediction["event_id"],
            "event_name": prediction["event_name"],
            "event_location": event["location"],
            "recipient_id": best_candidate["recipient_id"],
            "recipient_name": best_candidate["name"],
            "recipient_location": best_candidate["location"],
            "distance_km": best_candidate["distance_km"],
            "volume_kg": prediction["predicted_kg"],
            "food_category": food_category,
            "urgency": prediction["urgency"],
            "cost_score": best_candidate["cost_score"],
            "reasoning": reasoning,
            "alternatives": [
                {
                    "name": c["name"],
                    "distance_km": c["distance_km"],
                    "cost_score": c["cost_score"]
                }
                for c in candidates[1:3]  # Top 2 alternatives
            ]
        }
        
        return route
    
    def _score_candidates(self, 
                         event: dict, 
                         prediction: dict,
                         available_recipients: List[dict]) -> List[dict]:
        """
        Score and rank candidate recipients
        
        Returns list sorted by cost (lower = better)
        """
        candidates = []
        event_location = tuple(event["location"])
        is_perishable = prediction["category"] == "perishable"
        
        for recipient in available_recipients:
            recipient_location = tuple(recipient["location"])
            
            # Calculate distance
            distance = calculate_distance(event_location, recipient_location)
            
            # Check capacity
            capacity_check = check_recipient_capacity(
                recipient, 
                prediction["predicted_kg"]
            )
            
            if not capacity_check["can_accept"]:
                continue  # Skip if can't fit
            
            # Calculate routing cost
            cost = calculate_routing_cost(
                distance_km=distance,
                volume_kg=prediction["predicted_kg"],
                capacity_kg=recipient["capacity_kg"],
                is_perishable=is_perishable
            )
            
            candidates.append({
                **recipient,
                "distance_km": distance,
                "cost_score": cost,
                "capacity_check": capacity_check
            })
        
        # Sort by cost (lower is better)
        candidates.sort(key=lambda x: x["cost_score"])
        
        return candidates
    
    def _reason_about_route(self, 
                           prediction: dict,
                           event: dict, 
                           best_candidate: dict,
                           alternatives: List[dict]) -> str:
        """
        Use Nemotron to explain routing decision
        """
        alt_text = ""
        if alternatives:
            alt_text = "\nAlternatives considered:\n" + "\n".join([
                f"- {a['name']}: {a['distance_km']:.1f}km (cost: {a['cost_score']})"
                for a in alternatives
            ])
        
        user_prompt = f"""Analyze this routing decision:

Selected Match:
- Recipient: {best_candidate['name']}
- Distance: {best_candidate['distance_km']:.1f}km
- Cost Score: {best_candidate['cost_score']} (lower is better)
- Food: {prediction['predicted_kg']}kg {prediction['category']}
- Urgency: {prediction['urgency']}
{alt_text}

Explain in 1-2 sentences why this is the optimal match."""
        
        reasoning = self.think(self.system_prompt, user_prompt, temperature=0.6)
        return reasoning
    
    def _create_no_match_result(self, prediction: dict, reason: str) -> dict:
        """Create result for when no match is found"""
        return {
            "event_id": prediction["event_id"],
            "event_name": prediction["event_name"],
            "recipient_id": None,
            "recipient_name": "NO MATCH",
            "distance_km": 0,
            "volume_kg": prediction["predicted_kg"],
            "food_category": prediction["category"],
            "reasoning": f"Unable to route: {reason}",
            "alternatives": []
        }
    
    def format_log(self, route: dict) -> str:
        """Format route for logging"""
        if route["recipient_id"] is None:
            return self.log(f"⚠️  {route['event_name']}: {route['reasoning']}")
        
        return self.log(
            f"✅ {route['event_name']} → {route['recipient_name']}: "
            f"{route['distance_km']:.1f}km, {route['volume_kg']}kg {route['food_category']}"
        )

