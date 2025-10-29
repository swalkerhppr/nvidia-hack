"""
Quick test script for individual agents
"""
import json
from agents import PredictionAgent, RoutingAgent, OutreachAgent


def test_prediction_agent():
    """Test prediction agent in isolation"""
    print("\n🔍 Testing Prediction Agent...")
    print("-" * 60)
    
    # Load sample event
    with open('data/events.json', 'r') as f:
        events = json.load(f)
    
    event = events[0]
    print(f"Event: {event['name']}")
    print(f"  Attendees: {event['attendees']}")
    print(f"  Catering: {event['catering_type']}")
    
    # Run prediction
    agent = PredictionAgent()
    result = agent.analyze(event)
    
    print(f"\nResult:")
    print(f"  Has Surplus: {result['has_surplus']}")
    print(f"  Predicted: {result['predicted_kg']}kg")
    print(f"  Category: {result['category']}")
    print(f"  Confidence: {result['confidence']:.0%}")
    print(f"  Reasoning: {result['reasoning']}")
    
    print("\n✅ Prediction Agent Test Complete")
    return result


def test_routing_agent(prediction):
    """Test routing agent with prediction"""
    print("\n\n🚚 Testing Routing Agent...")
    print("-" * 60)
    
    # Load data
    with open('data/events.json', 'r') as f:
        events = json.load(f)
    with open('data/recipients.json', 'r') as f:
        recipients = json.load(f)
    
    event = events[0]
    
    # Run routing
    agent = RoutingAgent()
    result = agent.find_route(prediction, event, recipients)
    
    if result and result.get('recipient_id'):
        print(f"\nRoute Found:")
        print(f"  Recipient: {result['recipient_name']}")
        print(f"  Distance: {result['distance_km']:.1f}km")
        print(f"  Volume: {result['volume_kg']}kg {result['food_category']}")
        print(f"  Reasoning: {result['reasoning']}")
        print(f"  Alternatives: {[a['name'] for a in result['alternatives']]}")
    else:
        print("\n❌ No route found")
        result = None
    
    print("\n✅ Routing Agent Test Complete")
    return result


def test_outreach_agent(route):
    """Test outreach agent with route"""
    print("\n\n📧 Testing Outreach Agent...")
    print("-" * 60)
    
    if not route:
        print("❌ No route to generate message for")
        return
    
    # Run outreach
    agent = OutreachAgent()
    result = agent.generate_message(route)
    
    if result:
        print(f"\nMessage Generated:")
        print(f"  To: {result['recipient_name']}")
        print(f"  Urgency: {result['urgency_level']}")
        print(f"  Send Time: {result['estimated_send_time']}")
        print(f"\nMessage Content:")
        print("-" * 60)
        print(result['message_content'])
        print("-" * 60)
        print(f"\nStrategy: {result['strategy_reasoning']}")
    else:
        print("❌ No message generated")
    
    print("\n✅ Outreach Agent Test Complete")


def main():
    """Run all agent tests"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║           FeastGuard.AI - Agent Test Suite               ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Check for API key
    import os
    if not os.getenv("NVIDIA_API_KEY"):
        print("⚠️  Warning: NVIDIA_API_KEY not set in environment")
        print("   Please set your NVIDIA API key in .env file\n")
    
    try:
        # Test agents in sequence
        prediction = test_prediction_agent()
        
        if prediction and prediction['has_surplus']:
            route = test_routing_agent(prediction)
            
            if route:
                test_outreach_agent(route)
        
        print("\n\n" + "="*60)
        print("✅ ALL AGENT TESTS COMPLETED")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

