"""
Configuration Management for TruthLens Backend
Handles environment variables and AWS configuration
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List
import os


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    
    # Application Settings
    APP_NAME: str = "TruthLens Fake News Detection API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Model Configuration
    MODEL_PATH: str = "/mnt/e/AI ML/PROJECTS/TruthLens Multi-Modal Real-Time Fake News Detection System/Model-Trained/3810/"
    MAX_TEXT_LENGTH: int = 512
    CONFIDENCE_THRESHOLD: float = 0.5
    
    # Gemini API Configuration
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash-lite"
    GEMINI_TEMPERATURE: float = 0.3
    GEMINI_MAX_TOKENS: int = 300
    
    # AWS Configuration
    AWS_REGION: str = "ap-south-1"
    DYNAMODB_TABLE_NAME: str = "TruthLens-Predictions"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "truthlens.log"
    
    # CORS Settings - Use string that will be split
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8000"
    
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        # FIX: Disable protected namespaces warning
        protected_namespaces = ()
    
    def get_cors_origins(self) -> List[str]:
        """
        Convert comma-separated ALLOWED_ORIGINS to list
        """
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]


@lru_cache()
def get_settings() -> Settings:
    """
    Cached settings instance
    """
    return Settings()
