"""
Configuration settings for the AI Diagram Service.

Handles environment variables, API keys, and app settings.
Pretty straightforward config management using pydantic-settings.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    App settings - loads from env vars and .env file.
    
    Using pydantic-settings for automatic env var parsing.
    Much cleaner than manually handling os.getenv() everywhere.
    """
    
    # API Keys
    google_api_key: Optional[str] = None  # Gemini API key
    
    # Server config
    host: str = "0.0.0.0"  # Bind to all interfaces
    port: int = 8000
    debug: bool = False
    
    # File handling
    temp_dir: str = "./temp"  # Where to store generated diagrams
    max_file_size: int = 10485760  # 10MB limit
    
    # Logging
    log_level: str = "INFO"
    
    # Dev mode - useful for testing without API keys
    mock_llm: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = False  # Makes env var names more flexible


# Global instance - import this everywhere
settings = Settings() 