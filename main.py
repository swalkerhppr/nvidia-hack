"""
FeastGuard.AI - Main Runner
Multi-agent food redistribution system powered by NVIDIA Nemotron
"""
import json
import sys
from pathlib import Path
from orchestrator import FeastGuardOrchestrator
from agents import OutreachAgent


def load_json(filepath: str) -> list:
    """Load JSON data file"""
    with open(filepath, 'r') as f:
        return json.load(f)


def select_top_events(events: list, num: int = 5) -> list:
    """
    Select top N most interesting events for demo
    
    Prioritizes:
    - Large attendee count
    - Buffet catering (high surplus potential)
    - Diverse event types
    """
    # Sort by potential "interestingness"
    def score_event(event):
        score = 0
        score += event.get("attendees", 0) / 100  # Attendee weight
        score += 50 if event.get("catering_type") == "buffet" else 0
        score += 30 if event.get("catering_type") == "family_style" else 0
        score += event.get("duration_hours", 0) * 5
        return score
    
    sorted_events = sorted(events, key=score_event, reverse=True)
    return sorted_events[:num]


def print_header():
    """Print application header"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║              🍛  F E A S T G U A R D . A I  🍛             ║
║                                                           ║
║        Predictive Food Redistribution System              ║
║        Powered by NVIDIA Nemotron                         ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """)


def print_agent_logs(logs: list):
    """Pretty print agent logs"""
    print("\n📋 AGENT ACTIVITY LOG:")
    print("─" * 60)
    for log in logs:
        print(log)


def print_detailed_results(state: dict):
    """Print detailed results"""
    print("\n\n" + "="*60)
    print("📊 DETAILED RESULTS")
    print("="*60)
    
    # Predictions
    print("\n🔍 PREDICTIONS:")
    for pred in state["predictions"]:
        if pred["has_surplus"]:
            print(f"\n  Event: {pred['event_name']}")
            print(f"  └─ Surplus: {pred['predicted_kg']}kg ({pred['category']})")
            print(f"  └─ Urgency: {pred['urgency']} (confidence: {pred['confidence']:.0%})")
            print(f"  └─ Reasoning: {pred['reasoning'][:120]}...")
    
    # Routes
    print("\n\n🚚 ROUTES:")
    for route in state["routes"]:
        if route.get("recipient_id"):
            print(f"\n  {route['event_name']} → {route['recipient_name']}")
            print(f"  └─ Distance: {route['distance_km']:.1f}km")
            print(f"  └─ Volume: {route['volume_kg']}kg {route['food_category']}")
            print(f"  └─ Reasoning: {route['reasoning'][:120]}...")
            if route['alternatives']:
                print(f"  └─ Alternatives: {', '.join([a['name'] for a in route['alternatives']])}")
    
    # Messages
    print("\n\n📧 OUTREACH MESSAGES:")
    outreach_agent = OutreachAgent()
    for msg in state["messages"]:
        print(outreach_agent.format_message_for_display(msg))


def main():
    """Main execution"""
    print_header()
    
    # Check for data files
    events_file = Path("data/events.json")
    recipients_file = Path("data/recipients.json")
    
    if not events_file.exists() or not recipients_file.exists():
        print("❌ Error: Data files not found!")
        print("   Please run: python data/generate_data.py")
        sys.exit(1)
    
    # Load data
    print("📁 Loading data...")
    all_events = load_json(events_file)
    recipients = load_json(recipients_file)
    
    print(f"   Loaded {len(all_events)} events, {len(recipients)} recipients")
    
    # Select top 5 events for demo
    events = select_top_events(all_events, num=5)
    print(f"   Selected top 5 events for processing\n")
    
    # Initialize orchestrator
    print("🤖 Initializing multi-agent system...")
    orchestrator = FeastGuardOrchestrator()
    print("   ✅ Prediction Agent ready")
    print("   ✅ Routing Agent ready")
    print("   ✅ Outreach Agent ready")
    
    # Run workflow
    print("\n🚀 Starting workflow...\n")
    
    try:
        final_state = orchestrator.run(events, recipients)
        
        # Print logs
        print_agent_logs(final_state["agent_logs"])
        
        # Print detailed results
        print_detailed_results(final_state)
        
        # Success message
        print("\n\n" + "="*60)
        print("✅ WORKFLOW COMPLETED SUCCESSFULLY")
        print("="*60)
        print(f"\nProcessed {len(final_state['predictions'])} events")
        print(f"Generated {len(final_state['routes'])} routes")
        print(f"Created {len(final_state['messages'])} outreach messages")
        
        total_rescued = sum(r['volume_kg'] for r in final_state['routes'] if r.get('recipient_id'))
        print(f"\n🎯 Total Food Rescued: {total_rescued:.0f}kg")
        
        # Export results
        output_file = "results.json"
        with open(output_file, 'w') as f:
            json.dump({
                "predictions": final_state["predictions"],
                "routes": final_state["routes"],
                "messages": final_state["messages"],
                "logs": final_state["agent_logs"]
            }, f, indent=2)
        
        print(f"📄 Results saved to: {output_file}")
        
    except Exception as e:
        print(f"\n❌ Error during workflow execution:")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

