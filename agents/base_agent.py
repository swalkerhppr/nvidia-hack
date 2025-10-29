"""
Base agent utilities and shared functionality
"""
from typing import Dict, Any
import llm_client

class BaseAgent:
    """
    Base class for all FeastGuard agents
    
    Provides common utilities for reasoning and tool execution
    """
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.client = llm_client.get_client()
    
    def log(self, message: str) -> str:
        """Format agent log message"""
        return f"[{self.agent_name}] {message}"
    
    def think(self, system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
        """
        Call Nemotron for reasoning
        
        Args:
            system_prompt: Agent's role and instructions
            user_prompt: Specific task/question
            temperature: Sampling temperature
            
        Returns:
            Reasoning text from Nemotron
        """
        return self.client.chat_with_system(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=temperature
        )
    
    def extract_decision(self, reasoning_text: str, field: str) -> Any:
        """
        Extract structured decision from reasoning text
        
        Simple pattern matching - in production would use structured outputs
        """
        lines = reasoning_text.lower().split('\n')
        for line in lines:
            if field.lower() in line:
                # Extract value after colon or equals
                if ':' in line:
                    return line.split(':', 1)[1].strip()
                elif '=' in line:
                    return line.split('=', 1)[1].strip()
        return None

