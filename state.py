"""
State schema for LangGraph workflow
"""
from typing import TypedDict, List, Annotated, Literal
import operator

class AgentState(TypedDict):
    """
    Shared state across all agents in the workflow
    
    Uses Annotated with operator.add for accumulating lists
    """
    # Input data
    events: List[dict]
    recipients: List[dict]
    
    # Agent outputs (accumulated)
    predictions: Annotated[List[dict], operator.add]
    routes: Annotated[List[dict], operator.add]
    messages: Annotated[List[dict], operator.add]
    
    # Workflow control
    current_event_idx: int
    processed_events: Annotated[List[str], operator.add]  # event_ids
    
    # Logging for visibility (accumulated)
    agent_logs: Annotated[List[str], operator.add]
    
    # Metadata
    workflow_status: Literal["running", "completed", "error"]
    total_events: int


def create_initial_state(events: List[dict], recipients: List[dict]) -> AgentState:
    """
    Create initial state for workflow
    
    Args:
        events: List of event dictionaries
        recipients: List of recipient dictionaries
        
    Returns:
        Initial AgentState
    """
    return {
        "events": events,
        "recipients": recipients,
        "predictions": [],
        "routes": [],
        "messages": [],
        "current_event_idx": 0,
        "processed_events": [],
        "agent_logs": [],
        "workflow_status": "running",
        "total_events": len(events)
    }

