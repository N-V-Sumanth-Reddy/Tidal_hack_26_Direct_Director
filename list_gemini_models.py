"""
List available Gemini models
"""
import os
from dotenv import load_dotenv

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    print("❌ GEMINI_API_KEY not set")
    exit(1)

try:
    import google.genai as genai
    
    client = genai.Client(api_key=gemini_api_key)
    
    print("📋 Listing available models...\n")
    
    models = client.models.list()
    
    print("All models:")
    for model in models:
        print(f"  - {model.name}")
        if hasattr(model, 'supported_generation_methods'):
            print(f"    Methods: {model.supported_generation_methods}")
    
    print("\n🎨 Image generation models:")
    for model in models:
        if hasattr(model, 'supported_generation_methods'):
            if 'generateImages' in str(model.supported_generation_methods):
                print(f"  ✓ {model.name}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
