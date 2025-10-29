"""
LLM Client for NVIDIA Nemotron via OpenRouter
"""
import os
import requests
from typing import List, Dict, Optional, Generator
import config

class NemotronClient:
    """Wrapper for Nemotron API calls via OpenRouter"""
    
    def __init__(self):
        self.api_key = config.OPENROUTER_API_KEY
        self.model = "nvidia/nemotron-nano-12b-v2-vl"  # Updated model
        self.endpoint = config.OPENROUTER_ENDPOINT
        
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment")
    
    def chat(self, 
             messages: List[Dict[str, str]], 
             temperature: float = 0.7,
             max_tokens: int = 800) -> str:
        """
        Simple chat completion call
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Max response length
            
        Returns:
            Response content string
        """
        response = requests.post(
            self.endpoint,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://feastguard.ai",  # Optional: for OpenRouter analytics
                "X-Title": "FeastGuard.AI"
            },
            json={
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            },
            timeout=30
        )
        
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()
    
    def chat_with_system(self,
                        system_prompt: str,
                        user_prompt: str,
                        temperature: float = 0.7) -> str:
        """
        Convenience method for system + user prompt
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        return self.chat(messages, temperature=temperature)


# Global client instance
_client = None

def get_client() -> NemotronClient:
    """Get or create global Nemotron client"""
    global _client
    if _client is None:
        _client = NemotronClient()
    return _client

