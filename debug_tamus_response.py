"""
Debug script to see the exact TAMUS API response structure
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("TAMUS_API_KEY")
api_url = os.getenv("TAMUS_API_URL", "https://chat-api.tamu.ai")
model = os.getenv("TAMUS_MODEL", "protected.gpt-5.2")

url = f"{api_url}/api/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "Accept": "application/json",
}

body = {
    "model": model,
    "messages": [{"role": "user", "content": "Say hello"}],
    "max_tokens": 100,
    "temperature": 0.7,
    "stream": False,
}

print("="*60)
print("TAMUS API Response Debug")
print("="*60)
print(f"URL: {url}")
print(f"Model: {model}")
print(f"API Key: {api_key[:20]}...")
print()

try:
    response = requests.post(url, headers=headers, json=body, timeout=120)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Text Length: {len(response.text)} bytes")
    print()
    print("Raw Response Text:")
    print("-"*60)
    print(response.text)
    print("-"*60)
    print()
    
    if response.status_code == 200:
        try:
            data = response.json()
            print("Parsed JSON:")
            print("-"*60)
            import json
            print(json.dumps(data, indent=2))
            print("-"*60)
            print()
            
            if "choices" in data and data["choices"]:
                message = data["choices"][0].get("message", {})
                content = message.get("content")
                print(f"✓ Content extracted: {content}")
            else:
                print("✗ No 'choices' in response")
                
        except Exception as e:
            print(f"✗ JSON parsing failed: {e}")
    else:
        print(f"✗ HTTP error: {response.status_code}")
        
except Exception as e:
    print(f"✗ Request failed: {e}")
    import traceback
    traceback.print_exc()
