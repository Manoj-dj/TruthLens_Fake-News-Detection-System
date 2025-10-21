"""
Pydantic Models for Request/Response Validation
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict
from datetime import datetime


class NewsDetectionRequest(BaseModel):
    """
    Request model for fake news detection
    """
    title: str = Field(
        ..., 
        min_length=5, 
        max_length=500,
        description="News article title",
        example="BREAKING: Scientists Discover Miracle Cure"
    )
    text: str = Field(
        ..., 
        min_length=20, 
        max_length=10000,
        description="News article content",
        example="Amazing breakthrough that doctors don't want you to know..."
    )
    
    @validator('title', 'text')
    def validate_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Field cannot be empty or whitespace only")
        return v.strip()


class WordHighlight(BaseModel):
    """
    Word importance from SHAP analysis
    """
    word: str
    importance: float
    direction: str  # "fake" or "real"


class DetectionResponse(BaseModel):
    """
    Response model for fake news detection
    """
    success: bool
    prediction: str  # "Fake" or "Real"
    confidence: float
    fake_probability: float
    real_probability: float
    
    explanation: str
    word_highlights: List[WordHighlight]
    
    processing_time_ms: float
    timestamp: str
    request_id: str


class HealthResponse(BaseModel):
    """
    Health check response
    """
    status: str
    app_name: str
    version: str
    is_model_loaded: bool  # ← Changed from model_loaded
    timestamp: str
    
    class Config:
        protected_namespaces = ()  # ← Add this



class ErrorResponse(BaseModel):
    """
    Error response model
    """
    success: bool = False
    error: str
    error_type: str
    timestamp: str
    request_id: Optional[str] = None
