"""
Configuration for FeastGuard.AI Multi-Agent System
"""
import os
from dotenv import load_dotenv

load_dotenv()

# NVIDIA Nemotron Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
NEMOTRON_MODEL = "nvidia/nemotron-nano-12b-v2-vl"  # Updated model
OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"

# System Configuration
MAX_EVENTS = 50
MAX_RECIPIENTS = 20
MAX_DISTANCE_KM = 10
PERISHABLE_TIME_WINDOW_HOURS = 2

# Surplus Prediction Weights
SURPLUS_WEIGHTS = {
    "attendees": 0.3,
    "duration": 0.2,
    "catering_factor": 0.4,
    "weather_factor": 0.1
}

# Catering Type Factors
CATERING_FACTORS = {
    "buffet": 1.0,
    "plated": 0.5,
    "snacks": 0.2,
    "family_style": 0.8,
    "cocktail": 0.3
}

# Weather Impact
WEATHER_FACTORS = {
    "mild": 0.0,
    "hot": 0.1,
    "cold": -0.1,
    "rainy": -0.2
}

# Surplus Categories
SURPLUS_THRESHOLDS = {
    "none": (0.0, 0.3),
    "non_perishable": (0.3, 0.6),
    "perishable": (0.6, 1.0)
}

# Agent Configuration
AGENT_TEMPERATURE = 0.7
AGENT_MAX_ITERATIONS = 5

# UI Configuration
MAP_CENTER = [39.7392, -104.9903]  # Denver, CO
MAP_ZOOM = 11

