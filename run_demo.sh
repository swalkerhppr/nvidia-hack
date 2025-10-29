#!/bin/bash
# FeastGuard.AI Demo Launcher

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║        FeastGuard.AI - Demo Launcher                     ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Check if in venv
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Warning: Not in virtual environment"
    echo "   Run: source venv/bin/activate"
    echo ""
fi

# Check if results exist
if [ ! -f "results.json" ]; then
    echo "📊 No results found. Running workflow first..."
    echo ""
    python main.py
    echo ""
fi

# Launch results viewer
echo "🚀 Launching Results Viewer UI..."
echo ""
echo "📍 Open your browser to: http://localhost:8501"
echo ""
streamlit run results_viewer.py

