"""
Synthetic data generator for events and recipients
"""
import json
import random
from datetime import datetime, timedelta

# Denver metro area coordinates (roughly)
DENVER_LAT_RANGE = (39.60, 39.90)
DENVER_LON_RANGE = (-105.15, -104.75)

EVENT_TYPES = [
    "City Tech Conference",
    "Community Fundraiser",
    "Corporate Meeting",
    "Wedding Reception",
    "University Graduation",
    "Sports Tournament",
    "Music Festival",
    "Food Festival",
    "Trade Show",
    "Charity Gala",
    "School Event",
    "Religious Gathering",
    "Business Lunch",
    "Holiday Party",
    "Networking Mixer"
]

FOOD_TYPES = [
    ["sandwiches", "salads"],
    ["pizza", "pasta"],
    ["barbecue", "sides"],
    ["appetizers", "finger foods"],
    ["buffet", "mixed cuisine"],
    ["breakfast items", "pastries"],
    ["dinner entrees", "vegetables"],
    ["snacks", "beverages"],
]

CATERING_TYPES = ["buffet", "plated", "snacks", "family_style", "cocktail"]
WEATHER_OPTIONS = ["mild", "hot", "cold", "rainy"]

RECIPIENT_NAMES = [
    "Downtown Soup Kitchen",
    "Westside Community Pantry",
    "Highland Family Shelter",
    "Capitol Hill Food Bank",
    "Aurora Community Kitchen",
    "Northside Rescue Mission",
    "Denver Food Pantry Network",
    "Five Points Community Center",
    "Lakewood Family Services",
    "Englewood Helping Hands",
    "Cherry Creek Outreach",
    "Berkeley Neighborhood Kitchen",
    "Washington Park Community Center",
    "RiNo District Food Hub",
    "Green Valley Food Bank",
    "Stapleton Community Kitchen",
    "Golden Triangle Pantry",
    "Highlands Ranch Food Share",
    "Littleton Community Kitchen",
    "Westminster Family Center"
]

def generate_random_location():
    """Generate random lat/lon in Denver metro area"""
    lat = random.uniform(*DENVER_LAT_RANGE)
    lon = random.uniform(*DENVER_LON_RANGE)
    return [round(lat, 6), round(lon, 6)]

def generate_events(num_events=30):
    """Generate synthetic event data"""
    events = []
    base_date = datetime.now()
    
    for i in range(num_events):
        event_id = f"E{str(i+1).zfill(3)}"
        
        # Random event details
        event_type = random.choice(EVENT_TYPES)
        attendees = random.randint(50, 2000)
        catering_type = random.choice(CATERING_TYPES)
        food_type = random.choice(FOOD_TYPES)
        duration_hours = random.randint(2, 8)
        weather = random.choice(WEATHER_OPTIONS)
        
        # Random date within next 14 days
        event_date = base_date + timedelta(days=random.randint(0, 14))
        
        event = {
            "event_id": event_id,
            "name": f"{event_type} #{i+1}",
            "attendees": attendees,
            "catering_type": catering_type,
            "food_type": food_type,
            "duration_hours": duration_hours,
            "weather": weather,
            "date": event_date.strftime("%Y-%m-%d"),
            "location": generate_random_location(),
            "status": "upcoming"
        }
        
        events.append(event)
    
    return events

def generate_recipients(num_recipients=15):
    """Generate synthetic recipient organizations"""
    recipients = []
    
    for i in range(num_recipients):
        recipient_id = f"R{str(i+1).zfill(2)}"
        
        name = RECIPIENT_NAMES[i] if i < len(RECIPIENT_NAMES) else f"Community Center #{i+1}"
        
        # Random capacity
        capacity_kg = random.randint(50, 300)
        
        # Random current load (0-50% of capacity)
        current_load_kg = random.randint(0, capacity_kg // 2)
        
        # Random acceptance criteria
        accepts_perishable = random.choice([True, True, False])  # 66% accept perishable
        accepts_non_perishable = random.choice([True, True, True, False])  # 75% accept
        
        # Operating hours
        open_hour = random.randint(6, 9)
        close_hour = random.randint(17, 21)
        
        recipient = {
            "recipient_id": recipient_id,
            "name": name,
            "location": generate_random_location(),
            "capacity_kg": capacity_kg,
            "current_load_kg": current_load_kg,
            "accepts_perishable": accepts_perishable,
            "accepts_non_perishable": accepts_non_perishable,
            "operating_hours": f"{open_hour}:00-{close_hour}:00",
            "contact_available": True
        }
        
        recipients.append(recipient)
    
    return recipients

def save_data():
    """Generate and save synthetic data to JSON files"""
    events = generate_events(30)
    recipients = generate_recipients(15)
    
    with open("data/events.json", "w") as f:
        json.dump(events, f, indent=2)
    
    with open("data/recipients.json", "w") as f:
        json.dump(recipients, f, indent=2)
    
    print(f"✅ Generated {len(events)} events and {len(recipients)} recipients")
    print("📁 Saved to data/events.json and data/recipients.json")
    
    return events, recipients

if __name__ == "__main__":
    save_data()

