import os
import aiohttp
import json
from typing import List, Dict, Any, Optional
from .config import Config

class LLMClient:
    """Chutes-only LLM client."""
    
    def __init__(self, provider: str = "chutes"):
        self.provider = provider  # Always chutes
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def chat(
        self, 
        messages: List[Dict[str, str]], 
        model: Optional[str] = None,
        system_prompt: Optional[str] = None
    ) -> str:
        """Send chat request to Chutes API."""
        api_key = os.getenv("CHUTES_API_KEY")
        if not api_key:
            raise ValueError("CHUTES_API_KEY not set")
        
        url = "https://llm.chutes.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        chat_messages = []
        if system_prompt:
            chat_messages.append({"role": "system", "content": system_prompt})
        chat_messages.extend(messages)
        
        model_name = model or Config.DEFAULT_MODEL
        
        payload = {
            "model": model_name,
            "messages": chat_messages,
            "max_tokens": 2000
        }
        
        async with self.session.post(url, headers=headers, json=payload) as resp:
            text = await resp.text()
            
            if resp.status != 200:
                raise Exception(f"Chutes API error {resp.status}: {text}")
            
            data = json.loads(text)
            content = data["choices"][0]["message"].get("content")
            if content is None:
                print(f"[WARN] Model returned None - possible refusal. Full: {text[:300]}")
                return "..."
            return content.strip()