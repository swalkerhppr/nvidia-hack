# 🚀 FeastGuard.AI Setup Guide

## Phase 1 Implementation Complete ✅

Multi-agent food redistribution system powered by NVIDIA Nemotron.

---

## 📁 Project Structure

```
nvidia-hack/
├── agents/                    # Agent implementations
│   ├── prediction_agent.py   # Surplus prediction with Nemotron
│   ├── routing_agent.py      # Recipient matching optimization
│   └── outreach_agent.py     # Message generation
├── data/
│   ├── generate_data.py      # Synthetic data generator
│   ├── events.json           # Generated events
│   └── recipients.json       # Generated recipients
├── tools/                     # Utility functions
│   ├── surplus_calculator.py
│   ├── distance_calculator.py
│   ├── capacity_checker.py
│   └── message_generator.py
├── orchestrator.py           # LangGraph workflow coordinator
├── state.py                  # State schema
├── llm_client.py            # Nemotron API wrapper
├── config.py                # Configuration
├── main.py                  # Main runner
└── requirements.txt         # Dependencies
```

---

## 🔧 Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Key

Create a `.env` file in the project root:

```bash
OPENROUTER_API_KEY=your_api_key_here
```

**Get your free API key at:** https://openrouter.ai/keys

### 3. Generate Synthetic Data

```bash
python data/generate_data.py
```

This creates:
- `data/events.json` (30 events)
- `data/recipients.json` (15 recipients)

### 4. Run the Multi-Agent System

```bash
python main.py
```

This will:
- Load data
- Select top 5 "interesting" events
- Run the 3-agent workflow
- Display real-time agent logs
- Save results to `results.json`

---

## 🤖 Agent System Architecture

### **Workflow:**
```
Event → Prediction Agent → (if surplus) → Routing Agent → Outreach Agent
                                ↓
                            Agent Logs (visible reasoning)
```

### **Agents:**

1. **Prediction Agent**
   - Analyzes event attributes (attendees, catering, weather)
   - Uses Nemotron for reasoning
   - Calls `calculate_surplus_score()` and `estimate_food_volume()`
   - Output: Surplus prediction with confidence score

2. **Routing Agent**
   - Filters available recipients by capacity & food type
   - Calculates distances and routing costs
   - Uses Nemotron for optimization reasoning
   - Output: Optimal recipient match with alternatives

3. **Outreach Agent**
   - Generates context-aware coordination messages
   - Uses Nemotron for human-like communication
   - Adapts tone based on urgency
   - Output: Professional outreach message

### **Orchestrator:**
- LangGraph workflow coordinator
- Manages agent state and execution flow
- Logs agent reasoning for visibility
- Handles sequential processing of events

---

## 📊 Expected Output

### Agent Logs:
```
[Prediction Agent] 🔴 City Tech Conference: 120kg perishable surplus predicted (85%)
[Routing Agent] ✅ City Tech Conference → Downtown Soup Kitchen: 3.2km, 120kg perishable
[Outreach Agent] 🚨 Message for Downtown Soup Kitchen: 120kg perishable (send: immediate)
```

### Results File (`results.json`):
```json
{
  "predictions": [...],
  "routes": [...],
  "messages": [...],
  "logs": [...]
}
```

---

## 🎯 Key Features Implemented

✅ **3 Autonomous Agents** - Each with distinct reasoning capabilities  
✅ **Nemotron Integration** - Model: `nvidia/nemotron-nano-12b-v2-vl`  
✅ **Function Calling** - Agents use 7+ tool functions  
✅ **LangGraph Orchestration** - State-based workflow management  
✅ **ReAct Pattern** - Visible reasoning → action → observation loops  
✅ **Multi-step Workflows** - Prediction → Routing → Outreach  
✅ **Agent Logging** - Complete decision transparency  

---

## 🔍 Testing the System

### Quick Test (5 events):
```bash
python main.py
```

### Process All Events (30):
Edit `main.py` line 110:
```python
events = select_top_events(all_events, num=30)  # Change from 5 to 30
```

### Test Individual Agent:
```python
from agents import PredictionAgent
import json

agent = PredictionAgent()
event = json.load(open('data/events.json'))[0]
result = agent.analyze(event)
print(result)
```

---

## 🐛 Troubleshooting

### "OPENROUTER_API_KEY not found"
- Ensure `.env` file exists in project root
- Check API key is valid at https://openrouter.ai/keys

### "Data files not found"
```bash
python data/generate_data.py
```

### "Module not found" errors
```bash
pip install -r requirements.txt
```

### API Rate Limits
- OpenRouter free tier: ~10-20 requests/minute
- System processes 5 events by default (safe)
- Add delays if processing many events:
  ```python
  import time
  time.sleep(1)  # After each API call
  ```

---

## 📈 Next Steps (Phase 2 & 3)

**Phase 2:** Streamlit Dashboard (handled by teammate)
- Real-time agent activity visualization
- Interactive map with routes
- Agent reasoning display

**Phase 3:** Enhancements
- Multi-event batch optimization
- Agent "memory" across decisions
- Image classification for food verification
- Real weather API integration

---

## 🏆 NVIDIA Nemotron Prize Track Alignment

✅ **Agentic AI** - 3 autonomous agents with distinct roles  
✅ **Advanced Reasoning** - Nemotron powers decision-making  
✅ **Function Calling** - 7 tool functions integrated  
✅ **Multi-agent Orchestration** - LangGraph coordinator  
✅ **ReAct Loops** - Visible reasoning at each step  
✅ **Real-world Impact** - Food waste reduction use case  

---

## 📞 Support

Questions? Check:
- `NVIDIA_CONTEXT.md` - Prize track requirements
- `README.md` - Original project concept
- Agent code - Each has detailed docstrings

---

**Built with ❤️ for the NVIDIA Nemotron Hackathon**

