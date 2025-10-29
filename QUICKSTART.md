# 🚀 FeastGuard.AI - Quick Start

## Run in 3 Steps:

### 1️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 2️⃣ Set API Key
Create `.env` file:
```bash
echo "OPENROUTER_API_KEY=your_key_here" > .env
```
Get key at: https://openrouter.ai/keys

### 3️⃣ Run System
```bash
# Generate data (if not already done)
python data/generate_data.py

# Run the multi-agent system
python main.py
```

---

## 📊 What You'll See:

```
🍛 FEASTGUARD.AI
Predictive Food Redistribution System
Powered by NVIDIA Nemotron

📁 Loading data...
   Loaded 30 events, 15 recipients
   Selected top 5 events for processing

🤖 Initializing multi-agent system...
   ✅ Prediction Agent ready
   ✅ Routing Agent ready
   ✅ Outreach Agent ready

🚀 Starting workflow...

[Prediction Agent] 🔴 City Tech Conference: 120kg perishable (85%)
[Routing Agent] ✅ City Tech Conference → Downtown Soup Kitchen: 3.2km
[Outreach Agent] 🚨 Message for Downtown Soup Kitchen: immediate send

...

✅ WORKFLOW COMPLETED
Processed 5 events
Total Food Rescued: 380kg
📄 Results saved to: results.json
```

---

## 🧪 Test Individual Agents:
```bash
python test_agents.py
```

---

## 📖 Need More Details?
- `SETUP.md` - Full setup guide
- `PHASE1_COMPLETE.md` - Technical implementation details
- `NVIDIA_CONTEXT.md` - Prize track alignment

---

**That's it! 🎉**

