# 🏗️ FeastGuard.AI - System Architecture

## Phase 1: Core Agent System

---

## 📐 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      MAIN RUNNER (main.py)                  │
│  - Loads data (events.json, recipients.json)                │
│  - Selects top 5 events                                     │
│  - Initializes orchestrator                                 │
│  - Displays results                                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              ORCHESTRATOR (orchestrator.py)                 │
│  - LangGraph StateGraph                                     │
│  - Coordinates agent workflow                               │
│  - Manages state transitions                                │
│  - Logs agent decisions                                     │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
    ┌─────────┐    ┌─────────┐    ┌─────────┐
    │Prediction│    │ Routing │    │Outreach │
    │  Agent   │    │  Agent  │    │  Agent  │
    └─────┬────┘    └────┬────┘    └────┬────┘
          │              │              │
          └──────────────┼──────────────┘
                         ▼
         ┌───────────────────────────────┐
         │   NEMOTRON API (llm_client)    │
         │   - OpenRouter endpoint        │
         │   - nemotron-nano-12b-v2-vl    │
         └───────────────┬────────────────┘
                         │
         ┌───────────────┼────────────────┐
         ▼               ▼                ▼
    ┌─────────┐    ┌─────────┐    ┌──────────┐
    │ Surplus │    │Distance │    │ Message  │
    │  Tools  │    │  Tools  │    │   Tools  │
    └─────────┘    └─────────┘    └──────────┘
```

---

## 🔄 Workflow State Machine (LangGraph)

```
     START
       │
       ▼
  ┌─────────────┐
  │ PREDICTION  │──> Analyze event, predict surplus
  │    NODE     │
  └──────┬──────┘
         │
    Has surplus?
    ┌────┴────┐
    │         │
   YES       NO
    │         │
    ▼         └──> Next event (loop)
  ┌─────────────┐
  │   ROUTING   │──> Find best recipient match
  │    NODE     │
  └──────┬──────┘
         │
         ▼
  ┌─────────────┐
  │  OUTREACH   │──> Generate coordination message
  │    NODE     │
  └──────┬──────┘
         │
    More events?
    ┌────┴────┐
    │         │
   YES       NO
    │         │
    └──> Loop  ▼
         ┌─────────────┐
         │   SUMMARY   │──> Aggregate metrics
         │    NODE     │
         └──────┬──────┘
                │
                ▼
               END
```

---

## 🤖 Agent Architecture

### Prediction Agent
```
INPUT: Event dict
  {attendees, catering_type, duration, weather, ...}
       │
       ▼
┌─────────────────────────────────────────┐
│  Step 1: Nemotron Reasoning             │
│  "Buffet with 1000 guests → high waste" │
└────────────────┬────────────────────────┘
                 ▼
┌─────────────────────────────────────────┐
│  Step 2: calculate_surplus_score()      │
│  Score: 0.75 (perishable category)      │
└────────────────┬────────────────────────┘
                 ▼
┌─────────────────────────────────────────┐
│  Step 3: estimate_food_volume()         │
│  Volume: 120kg, Urgency: high          │
└────────────────┬────────────────────────┘
                 ▼
OUTPUT: Prediction dict
  {predicted_kg, category, confidence, reasoning}
```

### Routing Agent
```
INPUT: Prediction + Event + Recipients
       │
       ▼
┌─────────────────────────────────────────┐
│  Step 1: get_available_recipients()     │
│  Filter by food type & capacity         │
└────────────────┬────────────────────────┘
                 ▼
┌─────────────────────────────────────────┐
│  Step 2: calculate_distance() + costs   │
│  Score all candidates                   │
└────────────────┬────────────────────────┘
                 ▼
┌─────────────────────────────────────────┐
│  Step 3: Nemotron Reasoning             │
│  "Best match: closest + sufficient cap" │
└────────────────┬────────────────────────┘
                 ▼
OUTPUT: Route dict
  {recipient_id, distance_km, reasoning, alternatives}
```

### Outreach Agent
```
INPUT: Route dict
       │
       ▼
┌─────────────────────────────────────────┐
│  Step 1: Prepare context                │
│  {recipient, volume, urgency, distance} │
└────────────────┬────────────────────────┘
                 ▼
┌─────────────────────────────────────────┐
│  Step 2: generate_outreach_message()    │
│  (uses Nemotron for message generation) │
└────────────────┬────────────────────────┘
                 ▼
┌─────────────────────────────────────────┐
│  Step 3: Nemotron Strategy Reasoning    │
│  "Urgent tone for perishable food"      │
└────────────────┬────────────────────────┘
                 ▼
OUTPUT: Message dict
  {message_content, urgency_level, strategy_reasoning}
```

---

## 📦 Module Dependencies

```
main.py
  └─> orchestrator.py
       ├─> state.py (AgentState schema)
       ├─> agents/
       │    ├─> base_agent.py
       │    │     └─> llm_client.py
       │    │          └─> config.py
       │    ├─> prediction_agent.py
       │    │     └─> tools/surplus_calculator.py
       │    ├─> routing_agent.py
       │    │     └─> tools/distance_calculator.py
       │    │     └─> tools/capacity_checker.py
       │    └─> outreach_agent.py
       │          └─> tools/message_generator.py
       │               └─> llm_client.py
       └─> langgraph (StateGraph)
```

---

## 🔌 External Dependencies

### Python Packages:
- `langgraph` - State machine orchestration
- `langchain` - Agent utilities
- `requests` - API calls
- `python-dotenv` - Environment variables

### APIs:
- **OpenRouter** → NVIDIA Nemotron
  - Endpoint: `https://openrouter.ai/api/v1/chat/completions`
  - Model: `nvidia/nemotron-nano-12b-v2-vl`
  - Auth: Bearer token

---

## 📊 Data Flow

```
events.json (30 events)
recipients.json (15 recipients)
           ↓
      main.py (select top 5)
           ↓
   orchestrator.run()
           ↓
  ┌────────────────┐
  │ For each event │
  │   (5 total)    │
  └────────┬───────┘
           ↓
  ┌─────────────────────────────────┐
  │ Prediction → Route → Outreach   │
  │ (sequential processing)         │
  └────────┬────────────────────────┘
           ↓
  agent_logs[] (accumulated)
  predictions[] (accumulated)
  routes[] (accumulated)
  messages[] (accumulated)
           ↓
     results.json
```

---

## 🧠 Reasoning Patterns

### ReAct Loop (Prediction Agent Example):
```
1. REASON: "Large buffet event, likely waste"
   ↓
2. ACT: calculate_surplus_score(event)
   ↓
3. OBSERVE: "Score = 0.75 (perishable)"
   ↓
4. REASON: "High score, need volume estimate"
   ↓
5. ACT: estimate_food_volume(event, 0.75)
   ↓
6. OBSERVE: "120kg predicted"
   ↓
7. DECIDE: Return prediction with reasoning
```

---

## 🎯 State Management (LangGraph)

```python
AgentState = {
    # Input
    "events": List[dict],           # All events to process
    "recipients": List[dict],       # Available recipients
    
    # Agent outputs (accumulated with operator.add)
    "predictions": List[dict],      # Growing list
    "routes": List[dict],           # Growing list
    "messages": List[dict],         # Growing list
    "agent_logs": List[str],        # Growing list
    
    # Control
    "current_event_idx": int,       # Loop counter
    "workflow_status": str,         # "running"|"completed"
}
```

**Key Feature:** `Annotated[List, operator.add]`
- Enables list accumulation across nodes
- Each node appends to lists, not overwrites

---

## 🔐 Configuration

### config.py
```python
OPENROUTER_API_KEY      # From .env
NEMOTRON_MODEL          # "nvidia/nemotron-nano-12b-v2-vl"
MAX_DISTANCE_KM = 10    # Routing constraint
SURPLUS_WEIGHTS         # Prediction formula
CATERING_FACTORS        # Waste multipliers
```

---

## 🚀 Execution Path

1. **main.py** loads data, initializes orchestrator
2. **orchestrator.py** builds LangGraph workflow
3. For each event:
   - **prediction_node()** → calls PredictionAgent
   - **routing_node()** → calls RoutingAgent
   - **outreach_node()** → calls OutreachAgent
4. **summary_node()** → aggregates metrics
5. **main.py** displays results, saves JSON

**Total Flow:** ~5-10 Nemotron API calls (depends on surplus count)

---

## 🔍 Observability

### Agent Logs:
```python
agent_logs = [
    "[Prediction Agent] 🔴 Event: 120kg perishable (85%)",
    "[Routing Agent] ✅ Route: 3.2km to Downtown Kitchen",
    "[Outreach Agent] 🚨 Message: immediate send"
]
```

### Results JSON:
```json
{
  "predictions": [...],  // All predictions
  "routes": [...],       // All routes
  "messages": [...],     // All messages
  "logs": [...]          // All agent reasoning
}
```

---

## 🎨 Design Principles

1. **Separation of Concerns**
   - Agents focus on reasoning
   - Tools handle computation
   - Orchestrator manages flow

2. **Visible Reasoning**
   - Every decision logged
   - Nemotron outputs captured
   - Demo-friendly transparency

3. **Sequential Simplicity**
   - One event at a time
   - Clear state transitions
   - Easy to debug

4. **Tool-Augmented Intelligence**
   - Nemotron for reasoning
   - Python for calculation
   - Best of both worlds

---

**Built with 🧠 NVIDIA Nemotron + ⚙️ LangGraph**

