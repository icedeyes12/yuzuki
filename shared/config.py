import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Discord credentials
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN") or os.getenv("DISCORD_ID")
    
    # Bot owner - MUST be explicit
    OWNER_ID = os.getenv("OWNER_ID")
    OWNER_USERNAME = os.getenv("OWNER_USERNAME", "Owner")
    
    # LLM - Chutes only
    LLM_PROVIDER = "chutes"
    CHUTES_API_KEY = os.getenv("CHUTES_API_KEY")
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "Qwen/Qwen3.5-397B-A17B-TEE")
    MAX_HISTORY = int(os.getenv("MAX_HISTORY", "30"))
    
    # System prompt
    SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT")
    
    @classmethod
    def validate(cls):
        if not cls.DISCORD_TOKEN:
            raise ValueError("DISCORD_TOKEN not set!")
        if not cls.OWNER_ID:
            raise ValueError("OWNER_ID not set! Add your Discord User ID to Zo Secrets.")
        if not cls.CHUTES_API_KEY:
            raise ValueError("CHUTES_API_KEY not set!")