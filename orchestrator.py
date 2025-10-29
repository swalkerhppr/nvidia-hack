"""
LangGraph Orchestrator - Multi-agent workflow coordinator
"""
from typing import Dict, Literal
from langgraph.graph import StateGraph, END
from state import AgentState, create_initial_state
from agents import PredictionAgent, RoutingAgent, OutreachAgent


class FeastGuardOrchestrator:
    """
    Orchestrates multi-agent workflow for food redistribution
    
    Workflow:
    1. Load data
    2. For each event:
       - Prediction Agent analyzes surplus
       - If surplus exists:
         - Routing Agent finds best recipient
         - Outreach Agent generates message
    3. Summarize results
    """
    
    def __init__(self):
        self.prediction_agent = PredictionAgent()
        self.routing_agent = RoutingAgent()
        self.outreach_agent = OutreachAgent()
        
        # Build LangGraph workflow
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """
        Construct LangGraph state machine
        """
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("prediction", self.prediction_node)
        workflow.add_node("routing", self.routing_node)
        workflow.add_node("outreach", self.outreach_node)
        workflow.add_node("skip", self.skip_node)  # New node for no-surplus events
        workflow.add_node("summary", self.summary_node)
        
        # Define edges
        workflow.set_entry_point("prediction")
        
        # After prediction: check if we should route
        workflow.add_conditional_edges(
            "prediction",
            self.should_route,
            {
                "route": "routing",
                "skip": "skip",  # Go to skip node to increment counter
                "done": "summary"
            }
        )
        
        # After skip: loop back to next event or finish
        workflow.add_conditional_edges(
            "skip",
            self.should_continue,
            {
                "continue": "prediction",
                "done": "summary"
            }
        )
        
        # After routing: always do outreach
        workflow.add_edge("routing", "outreach")
        
        # After outreach: loop back to next event or finish
        workflow.add_conditional_edges(
            "outreach",
            self.should_continue,
            {
                "continue": "prediction",
                "done": "summary"
            }
        )
        
        # Summary is final
        workflow.add_edge("summary", END)
        
        return workflow.compile()
    
    def prediction_node(self, state: AgentState) -> Dict:
        """
        Run Prediction Agent on current event
        """
        current_idx = state["current_event_idx"]
        
        # Check if we're done
        if current_idx >= len(state["events"]):
            return {"workflow_status": "completed"}
        
        event = state["events"][current_idx]
        
        # Log start
        log_start = f"\n{'='*60}\n🔍 Processing Event {current_idx + 1}/{len(state['events'])}: {event['name']}\n{'='*60}"
        
        # Run prediction
        prediction = self.prediction_agent.analyze(event)
        
        # Format log
        log_result = self.prediction_agent.format_log(prediction)
        
        return {
            "predictions": [prediction],
            "agent_logs": [log_start, log_result],
            "processed_events": [event["event_id"]]
        }
    
    def routing_node(self, state: AgentState) -> Dict:
        """
        Run Routing Agent on latest prediction
        """
        current_idx = state["current_event_idx"]
        event = state["events"][current_idx]
        prediction = state["predictions"][-1]  # Latest prediction
        
        # Run routing
        route = self.routing_agent.find_route(
            prediction=prediction,
            event=event,
            recipients=state["recipients"]
        )
        
        if route is None:
            # No surplus to route
            return {
                "agent_logs": [self.routing_agent.log("⚪ No routing needed (no surplus)")]
            }
        
        # Format log
        log_result = self.routing_agent.format_log(route)
        
        return {
            "routes": [route],
            "agent_logs": [log_result]
        }
    
    def skip_node(self, state: AgentState) -> Dict:
        """
        Handle events with no surplus - increment counter and continue
        """
        current_idx = state["current_event_idx"]
        new_idx = current_idx + 1
        
        log_msg = f"⚪ No surplus detected - moving to next event"
        
        return {
            "agent_logs": [log_msg],
            "current_event_idx": new_idx
        }
    
    def outreach_node(self, state: AgentState) -> Dict:
        """
        Run Outreach Agent on latest route
        """
        current_idx = state["current_event_idx"]
        new_idx = current_idx + 1
        
        # Get latest route
        if not state["routes"]:
            return {
                "agent_logs": [self.outreach_agent.log("⚪ No message needed")],
                "current_event_idx": new_idx  # ALWAYS increment!
            }
        
        route = state["routes"][-1]
        
        # Generate message
        message = self.outreach_agent.generate_message(route)
        
        if message is None:
            return {
                "agent_logs": [self.outreach_agent.log("⚪ No recipient matched")],
                "current_event_idx": new_idx  # ALWAYS increment!
            }
        
        # Format log
        log_result = self.outreach_agent.format_log(message)
        
        # Increment counter for next event
        return {
            "messages": [message],
            "agent_logs": [log_result],
            "current_event_idx": new_idx
        }
    
    def summary_node(self, state: AgentState) -> Dict:
        """
        Generate final summary
        """
        predictions = state["predictions"]
        routes = state["routes"]
        messages = state["messages"]
        
        # Calculate metrics
        total_events = len(predictions)
        events_with_surplus = sum(1 for p in predictions if p["has_surplus"])
        successful_routes = sum(1 for r in routes if r.get("recipient_id") is not None)
        total_kg_rescued = sum(r["volume_kg"] for r in routes if r.get("recipient_id") is not None)
        
        perishable_count = sum(1 for r in routes if r.get("food_category") == "perishable" and r.get("recipient_id"))
        non_perishable_count = sum(1 for r in routes if r.get("food_category") == "non_perishable" and r.get("recipient_id"))
        
        # Format summary
        summary_log = f"""
{'='*60}
📊 WORKFLOW SUMMARY
{'='*60}
Events Processed: {total_events}
Events with Surplus: {events_with_surplus}
Successful Routes: {successful_routes}
Total Food Rescued: {total_kg_rescued:.0f}kg

Food Categories:
  - Perishable: {perishable_count} routes
  - Non-perishable: {non_perishable_count} routes

Messages Generated: {len(messages)}
{'='*60}
"""
        
        return {
            "agent_logs": [summary_log],
            "workflow_status": "completed"
        }
    
    def should_route(self, state: AgentState) -> Literal["route", "skip", "done"]:
        """
        Decide if we should route or skip
        """
        current_idx = state["current_event_idx"]
        num_events = len(state["events"])
        
        # Check if done processing
        if current_idx >= num_events:
            return "done"
        
        # Check if latest prediction has surplus
        if state["predictions"]:
            latest = state["predictions"][-1]
            if latest["has_surplus"]:
                return "route"
        
        # No surplus, increment and continue
        return "skip"
    
    def should_continue(self, state: AgentState) -> Literal["continue", "done"]:
        """
        Decide if we should process more events
        """
        current_idx = state["current_event_idx"]
        num_events = len(state["events"])
        
        if current_idx >= num_events:
            return "done"
        
        return "continue"
    
    def run(self, events: list, recipients: list) -> AgentState:
        """
        Run the complete workflow
        
        Args:
            events: List of event dictionaries
            recipients: List of recipient dictionaries
            
        Returns:
            Final state with all results
        """
        # Create initial state
        initial_state = create_initial_state(events, recipients)
        
        # Execute workflow with increased recursion limit
        # Each event can take 3-4 nodes (prediction, routing, outreach, skip)
        # So 5 events * 4 = 20 nodes minimum, set to 100 for safety
        final_state = self.workflow.invoke(
            initial_state,
            config={"recursion_limit": 100}
        )
        
        return final_state

