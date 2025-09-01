#!/usr/bin/env python3
"""
Configuration management for 4-Plex Unified Platform
"""

import os
from typing import Any, Dict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    
    # Database Configuration
    postgres_password: str = "4plex_postgres_2024_secure!"
    redis_password: str = "4plex_redis_2024_secure!"
    neo4j_password: str = "4plex_neo4j_2024_secure!"
    
    # AI API Keys
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    gemini_api_key: str = ""
    groq_api_key: str = ""
    
    # Application Settings
    log_level: str = "INFO"
    debug: bool = False
    
    # Service URLs
    discovery_endpoint: str = "http://discovery-engine:11050"
    valuation_endpoint: str = "http://valuation-engine:11060"
    
    model_config = {"env_file": ".env", "case_sensitive": False}

def get_settings() -> Settings:
    """Get application settings"""
    return Settings()