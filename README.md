.

🍛 PROJECT: “FeastGuard.AI” — Predictive Food Redistribution Simulator
🎯 Core Idea

An AI agent system that:

Uses synthetic event data to predict if and what food will be left over after events.

Determines the best redistribution route based on food type (perishable vs. non-perishable), location, and recipient capacity.

Optionally conducts outreach simulation — generating polite, human-like messages to organizers or recipients.

No scraping, no real data ingestion — just AI-generated mock data that mirrors plausible real-world patterns.

🧩 Core Components
Component	Role	Implementation Sketch
🗓️ Event Generator	Produces mock events: type, size, cuisine, date, and location.	Generate 50–100 random entries using rule-based generator or small LLM prompts (e.g., “community fundraiser, 200 guests, barbecue catering”).
🍱 Surplus Predictor Model	Estimates if leftover food exists and how much, by type.	Simple ML regression or heuristic model: surplus_likelihood = f(guests, catering_type, weather, event_type).
Outputs probabilities for: none / perishable / non-perishable.
🚚 Routing Model	Assigns predicted surplus to best recipient: pantry, soup kitchen, or shelter.	Use mock dataset of 10–20 recipient orgs (location, capacity, accepted food type, hours).
Apply simple distance-weighted or constraint-based optimization.
📦 Logistics Simulator	Simulates pickup and delivery timing, optional volunteer routing.	Basic path or queue simulation, visualize flow lines on map (Streamlit or matplotlib).
💬 Outreach Generator (Stretch)	Auto-drafts messages to event hosts or recipient orgs.	Use Nemotron or NIM text generation to produce friendly coordination notes.
📊 Data Design (All Synthetic)
🧾 Example Event Record
{
  "event_id": "E015",
  "name": "City Tech Conference",
  "attendees": 1800,
  "catering_type": "buffet",
  "food_type": ["sandwiches", "salads"],
  "duration_hours": 6,
  "weather": "mild",
  "predicted_surplus_kg": 120,
  "surplus_category": "perishable"
}

🏢 Example Recipient Record
{
  "recipient_id": "R04",
  "name": "Downtown Soup Kitchen",
  "location": "Denver, CO",
  "capacity_kg": 150,
  "accepts_perishable": true,
  "accepts_non_perishable": false
}

⚙️ Model Logic
1️⃣ Surplus Prediction

Simplified logic:

surplus_score = 0.3*(attendees/1000) + 0.2*(event_duration/5) + 0.4*(catering_factor) - 0.1*(weather_factor)


Output categories:

0.0–0.3 → No surplus

0.3–0.6 → Mostly non-perishables

0.6–1.0 → High perishable surplus

catering_factor could be rule-based (buffet = 1.0, plated = 0.5, snacks = 0.2).

2️⃣ Routing Decision

Optimization rule:

Filter recipients by accepts_perishable == True/False.

Compute distance between event and recipient (mock lat/long).

Sort by distance / capacity.

Assign best match.

This can be modeled as a cost minimization:

cost = (distance_km * perishability_weight) / recipient_capacity

3️⃣ Outreach (Stretch)

Generate sample messages using Nemotron:

“Hi [Organizer Name],
We’ve detected your event TechFest 2025 might have surplus fresh food. Would you like to connect with nearby kitchens for donation pickup within 2 hours post-event?”

Even if simulated, this demonstrates the conversational agent’s social impact.

🧠 Possible AI Components (for NVIDIA Integration)
Task	AI Role	NVIDIA Stack
Synthetic data generation	Produce plausible event/recipient data	NIM or small LLM fine-tuned for structured outputs
Surplus classification	Simple NIM model (binary + regression)	NIM + MCP
Routing logic	Optimization / reasoning agent	NIM reasoning node
Outreach message generation	Polite, context-aware text	Nemotron
Visualization	Real-time simulation dashboard	GPU-accelerated maps / charts
🎨 Demo Flow for Hackathon

Step 1: Generate 20 upcoming events (mock data).

Step 2: Run surplus prediction model → color-coded results (Red = High surplus, Green = Low).

Step 3: Route perishable surplus to soup kitchens; non-perishable to pantries.

Step 4: Display map animation showing food “flows.”

Step 5 (Stretch): Show AI-generated outreach message sample.

Step 6: Final dashboard summary:

250 kg surplus rescued

5 pantries supplied

3 soup kitchens reached

📈 Impact Metrics to Simulate

% of events producing surplus

% successfully routed within distance threshold

Total “meals recovered”

% perishable vs. non-perishable

Average travel time (km saved via optimization)

💬 2-Minute Pitch Script (Condensed)

“Every large event ends with uneaten food — not because people don’t care, but because coordination comes too late.
FeastGuard.AI predicts surplus before it happens.
Using NVIDIA NIM for reasoning and Nemotron for language, we simulate how an AI agent can forecast food excess from event attributes, classify it as perishable or not, and route it to the best recipients automatically.
Our demo generates realistic mock data — no scraping — and shows real-time optimization of surplus redistribution.
The result: smarter logistics, fewer wasted meals, and a model that cities and nonprofits could scale in the real world.”

🚀 Stretch Goals

Multi-agent coordination: independent restaurant + event + volunteer sub-agents managed via MCP.

Image classifier: simulate photo input of leftovers to verify perishable types.

Real-time feedback loop: pantry confirms receipt, updates future model predictions