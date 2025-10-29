# 🏆 NVIDIA Nemotron - Hackathon Context

## Prize Track: Best Use of NVIDIA Nemotron

**Focus:** Agentic AI systems that reason, plan, and take action autonomously

---

## Why Nemotron?

Nemotron is purpose-built for **agentic AI**, not just chat:

✅ **Advanced reasoning** and multi-step problem-solving  
✅ **Function calling** to interact with external tools/APIs  
✅ **Autonomous decision-making** within agent workflows  
✅ **Multi-agent orchestration** where specialized agents collaborate  
✅ **ReAct pattern** (Reason → Act → Observe loops)

---

## Recommended Models

- **Nemotron-nano-9b-v2** - Fast, efficient, perfect for hackathons
- **Nemotron-super-49b-v1_5** - More powerful reasoning
- **🆕 Nemotron-Nano-12B-v2-VL** - Visual + language
- **🆕 Nemotron-Safety-Guard-8B-v3** - Safety filtering

---

## Access Methods

### 1. OpenRouter API (Fastest Start ⚡)
```bash
export OPENROUTER_API_KEY="your-key"
```
Endpoint: `https://openrouter.ai/api/v1/chat/completions`  
Model: `nvidia/nemotron-nano-9b-v2`

### 2. Hugging Face (Open Weights)
```bash
pip install transformers torch
```
Model: `nvidia/nvidia-nemotron-nano-9b-v2`

### 3. NVIDIA NIM (Production-Ready)
Optimized inference platform

---

## Key Frameworks

- **LangGraph** - Agent orchestration and state management
- **LangChain** - Tool calling and chains
- **Tavily** - Web search capabilities

---

## What Judges Look For

✅ **Autonomous reasoning** - Agents decide, not just respond  
✅ **Multi-step workflows** - Complex task execution  
✅ **Tool integration** - Smart use of external functions/APIs  
✅ **Real-world applicability** - Solves actual problems  
✅ **Visible thinking** - Show agent decision-making process in demo

---

## Resources

- [Report Generator Agent Tutorial](https://github.com/NVIDIA/GenerativeAIExamples)
- [Agentic RAG Tutorial](https://github.com/NVIDIA/GenerativeAIExamples)
- [Developer Forums](https://discord.gg/nvidia)
- [Technical Docs](https://developer.nvidia.com/nemotron)

---

## Our Implementation: FeastGuard.AI

**Multi-Agent System for Food Redistribution:**

1. **Prediction Agent** - Analyzes events, predicts surplus
2. **Routing Agent** - Optimizes recipient matching
3. **Outreach Agent** - Generates coordination messages
4. **Orchestrator** - Coordinates agent workflow

**Why This Fits Nemotron:**
- Autonomous decision-making across 3+ agents
- Function calling for tools (distance, capacity, weather)
- ReAct loops for adaptive reasoning
- Real-world impact (food waste reduction)

