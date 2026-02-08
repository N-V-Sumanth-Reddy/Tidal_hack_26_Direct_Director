"""
TAMUS API Wrapper for Ad Video Pipeline
Provides integration with TAMU Gemini 2.5 Flash model

Based on the working TAMUS API wrapper for Claude-compatible systems.
Adapted for Gemini models and ad video generation use case.

Author: Ad Video Pipeline
Date: 2025-02-07
"""

import os
import json
import requests
from typing import Optional, Dict, Any, List
from dataclasses import dataclass


@dataclass
class TAMUSConfig:
    """Configuration for TAMUS API connection"""
    api_key: str
    api_base: str = "https://chat-api.tamu.ai"
    model: str = "protected.gemini-2.5-flash"
    timeout: int = 300  # Increased to 5 minutes for complex production planning


class TAMUSAPIClient:
    """Wrapper client for TAMUS API that mimics Anthropic/Gemini client interface"""
    
    def __init__(self, config: TAMUSConfig):
        self.config = config
        self.base_url = config.api_base
        self.headers = {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
    
    def _call_openai_compatible_endpoint(
        self,
        messages: List[Dict[str, Any]],
        model: str,
        max_tokens: int = 4000,
        temperature: float = 0.7,
    ) -> str:
        """Call TAMUS API using OpenAI-compatible endpoint"""
        url = f"{self.base_url}/api/v1/chat/completions"
        
        body = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False,
        }
        
        print(f"[TAMUS] POST {url}")
        print(f"[TAMUS] Model: {model}")
        
        try:
            response = requests.post(
                url,
                headers=self.headers,
                json=body,
                timeout=self.config.timeout,
            )
            
            print(f"[TAMUS] Status: {response.status_code}")
            print(f"[TAMUS] Response length: {len(response.text)} bytes")
            
            if response.status_code != 200:
                print(f"[TAMUS] Error: {response.text}")
                response.raise_for_status()
            
            # Check if response is empty
            if not response.text or response.text.strip() == "":
                print(f"[TAMUS] ⚠ Empty response body (status 200 but no content)")
                print(f"[TAMUS] Request details:")
                print(f"  - Model: {model}")
                print(f"  - Max tokens: {max_tokens}")
                print(f"  - Temperature: {temperature}")
                print(f"  - Message length: {len(str(messages))} chars")
                raise ValueError("Empty response body from API")
            
            data = response.json()
            
            if "choices" not in data or not data["choices"]:
                print(f"[TAMUS] ⚠ Unexpected response format")
                print(f"[TAMUS] Response keys: {list(data.keys())}")
                print(f"[TAMUS] Response preview: {str(data)[:200]}")
                raise ValueError(f"Unexpected response format: {data}")
            
            message = data["choices"][0].get("message", {})
            content = message.get("content")
            
            # Check if content is empty string (not just None)
            if not content or content.strip() == "":
                print(f"[TAMUS] ⚠ Empty content in message")
                print(f"[TAMUS] Message keys: {list(message.keys())}")
                print(f"[TAMUS] Message: {message}")
                print(f"[TAMUS] Full response data: {data}")
                
                # Check if there's a finish_reason that explains why
                finish_reason = data["choices"][0].get("finish_reason")
                if finish_reason:
                    print(f"[TAMUS] Finish reason: {finish_reason}")
                
                # Check for content filter
                if "content_filter_results" in str(data):
                    print(f"[TAMUS] ⚠ Content may have been filtered")
                
                raise ValueError(f"No content in response (finish_reason: {finish_reason})")
            
            print(f"[TAMUS] ✓ Success: {len(content)} chars returned")
            return content
            
        except requests.RequestException as e:
            print(f"[TAMUS] Request failed: {e}")
            raise
        except (KeyError, ValueError) as e:
            print(f"[TAMUS] Parse failed: {e}")
            raise
    
    def messages(self):
        """Provide messages interface"""
        return MessagesInterface(self)


class MessagesInterface:
    """Mimics Anthropic's client.messages interface for compatibility"""
    
    def __init__(self, client: TAMUSAPIClient):
        self.client = client
    
    def create(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        max_tokens: int = 4000,
        **kwargs
    ) -> "MessageResponse":
        """Create a completion using TAMUS API"""
        processed_messages = self._process_messages(messages)
        temperature = kwargs.get("temperature", 0.7)
        
        content = self.client._call_openai_compatible_endpoint(
            messages=processed_messages,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        
        return MessageResponse(content=content)
    
    def _process_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process messages to ensure compatibility with TAMUS API"""
        processed = []
        
        for msg in messages:
            if msg.get("role") not in ["user", "assistant", "system"]:
                continue
            
            if isinstance(msg.get("content"), list):
                # Handle multimodal content
                content_parts = []
                for item in msg["content"]:
                    if isinstance(item, dict):
                        if item.get("type") == "text":
                            content_parts.append({
                                "type": "text",
                                "text": item.get("text", "")
                            })
                        elif item.get("type") == "image_url":
                            # Pass through image_url directly
                            content_parts.append(item)
                
                processed.append({
                    "role": msg["role"],
                    "content": content_parts
                })
            else:
                processed.append({
                    "role": msg["role"],
                    "content": msg.get("content", "")
                })
        
        return processed


class MessageResponse:
    """Response wrapper that mimics Anthropic response format"""
    
    def __init__(self, content: str):
        self.content = [{"type": "text", "text": content}]
        self._text = content
    
    def __getitem__(self, index):
        return self.content[index]
    
    @property
    def text(self):
        return self._text


def get_tamus_client(
    api_key: Optional[str] = None,
    api_base: Optional[str] = None,
    model: Optional[str] = None,
) -> TAMUSAPIClient:
    """Factory function to create TAMUS API client.
    
    Args:
        api_key: TAMUS API key (defaults to TAMUS_API_KEY env var)
        api_base: TAMUS API base URL (defaults to TAMUS_API_URL env var)
        model: Model name (defaults to TAMUS_MODEL env var)
    
    Returns:
        TAMUSAPIClient instance
        
    Raises:
        ValueError: If TAMUS credentials are incomplete
    """
    key = api_key or os.getenv("TAMUS_API_KEY")
    if not key:
        raise ValueError(
            "TAMUS_API_KEY not set. "
            "Please set TAMUS_API_KEY environment variable."
        )
    
    base = api_base or os.getenv("TAMUS_API_URL", "https://chat-api.tamu.ai")
    model_name = model or os.getenv("TAMUS_MODEL", "protected.gemini-2.5-flash")
    
    config = TAMUSConfig(
        api_key=key,
        api_base=base,
        model=model_name,
    )
    
    return TAMUSAPIClient(config)


# Demo/test function
if __name__ == "__main__":
    try:
        client = get_tamus_client()
        print("[Demo] TAMUS client initialized!")
        
        response = client.messages().create(
            model=os.getenv("TAMUS_MODEL", "protected.gemini-2.5-flash"),
            messages=[{"role": "user", "content": "Say HELLO"}],
            max_tokens=100,
        )
        
        print(f"[Demo] Response: {response.content[0]['text']}")
    except Exception as e:
        print(f"[Demo] Error: {e}")

