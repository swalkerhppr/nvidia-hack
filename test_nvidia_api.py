"""
Quick test to verify NVIDIA API key is working
"""
import os
from dotenv import load_dotenv
import requests

load_dotenv()

def test_nvidia_api():
    """Test NVIDIA API connection"""
    api_key = os.getenv("NVIDIA_API_KEY")
    
    if not api_key:
        print("❌ Error: NVIDIA_API_KEY not found in environment")
        print("Please add it to your .env file")
        return False
    
    print("🔑 API Key found, testing connection...")
    print(f"   Key prefix: {api_key[:15]}...")
    
    # Make test request
    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    
    payload = {
        "model": "nvidia/nemotron-nano-12b-v2-vl",
        "messages": [
            {"role": "user", "content": "Say 'Hello from NVIDIA!' in one sentence."}
        ],
        "temperature": 0.7,
        "max_tokens": 50,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "top_p": 1
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "accept": "application/json",
        "content-type": "application/json"
    }
    
    try:
        print("📡 Sending test request to NVIDIA API...")
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            print(f"\n✅ Success! Response from NVIDIA Nemotron:")
            print(f"   {content}\n")
            return True
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(f"   Response: {response.text}\n")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Request failed: {e}\n")
        return False

if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════╗
║           NVIDIA API Connection Test                      ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    success = test_nvidia_api()
    
    if success:
        print("🎉 NVIDIA API is configured correctly!")
        print("   You can now run: python test_agents.py")
    else:
        print("⚠️  Please check your NVIDIA_API_KEY and try again")

